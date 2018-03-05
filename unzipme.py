#!/usr/bin/python
import argparse
import fnmatch
import getpass
import os
import subprocess
import time
import zipfile
import progressbar


def main():
    """starts the collection of files in the directory it's ran from.
    """
    args = parse_args()
    if args.verbose:
        print 'verbose mode enabled'
        time.sleep(1)
    if args.type:
        star = '*'
        period = '.'
        if args.type[0] != star:
            if args.type[0] == period:
                args.type = star + args.type
            elif args.type[0] != period:
                args.type = star + period + args.type
    progress(args.type, args.verbose)


def parse_args():
    """Parses optional args and shows menu.

    :return: args passed from command line.

    """
    parser = argparse.ArgumentParser(
        description='**************************** unzipme help menu ***************************** '
                    'Finds compressed files from directory ran and extracts them to ./EXTRACTED \n\n'
                    'Supports: *.zip, *.tgz, *.gz, *.xz, *.bz2, *.tbz, *.tbz2, *.tar, *.Z, *.rar')

    #Optional Arguments
    parser.add_argument("-v", "--verbose", help="Increase output verbosity. Default: False",
                        action="store_true")
    parser.add_argument('-t', '--type', default=False, metavar='',
                        help='Extracts specific compressed file format only. Default: False')
    args = parser.parse_args()
    return args

def progress(compressed_type, verbose=False):
    """Displays progress of compressed files found and extracted.

    """
    file_list = find_compressed_files_in_folder(compressed_type)
    bundle_length = len(file_list)
    if bundle_length > 1 and not bundle_length < 0 and not compressed_type:
        answer = raw_input("{}, files found, extract? (Y/N): ".format(bundle_length))
        if answer.lower() == 'y':
            set_file_permissions(file_list, verbose)
            pbar = progressbar.ProgressBar(
                widgets=[progressbar.Percentage(), ' ', progressbar.SimpleProgress(), progressbar.Bar()])
            for n in pbar(range(bundle_length)):
                extract_file(file_list[n])
                time.sleep(.2)
            set_extract_permisions(verbose)
            print '   files extract to: {}/EXTRACT'.format(os.getcwd())
        else:
            print 'Files not extracted, exiting unzipme.'
            exit(0)

    elif bundle_length > 1 and not bundle_length < 0 and compressed_type:
        answer = raw_input("{}, {} files found, extract? (Y/N): ".format(bundle_length, compressed_type))
        if answer.lower() == 'y':
            set_file_permissions(file_list, verbose)
            pbar = progressbar.ProgressBar(
                widgets=[progressbar.Percentage(), ' ', progressbar.SimpleProgress(), progressbar.Bar()])
            for n in pbar(range(bundle_length)):
                extract_file(file_list[n])
                time.sleep(.2)
            set_extract_permisions(verbose)
            print '   Files extract to: {}/EXTRACTED/'.format(os.getcwd())
        else:
            print 'Files not extracted, exiting unzipme.'
            exit(0)


    elif bundle_length == 1:
        answer = raw_input("{} file found, extract? (Y/N): ".format(bundle_length))
        if answer.lower() == 'y':
            set_file_permissions(file_list, verbose)
            if extract_file(file_list[0]):
                print "File '{}' extracted".format(os.path.basename(file_list[0]))
                set_extract_permisions(verbose)
                exit(0)
            else:
                print "File '{}' could not be extracted".format(os.path.basename(file_list[0]))
                exit(0)
        else:
            print 'Files not extracted, exiting unzipme.'
            exit(0)
    else:
        print 'no compressed files found in {}'.format(os.getcwd())
        exit(0)


def set_file_permissions(bundle_list, verbose=False):
    """Checks and sets permissions to compressed/zipped file.
    """
    try:
        if verbose:
            print 'setting permission to files found\n'
        for i in bundle_list:
            os.chmod(i, 0777)
        return
    except os.error:
        answer = raw_input("'Could not Apply permissions to file(s), try to extract anyway?' (Y/N): ")
        if answer.lower() == 'y':
            return
        else:
            exit(0)

def find_compressed_files_in_folder(file_type, verbose=False):
    """Finds compressed files in directory, returns them as a list.

    SUPPORTED FORMATS: *.zip', '*.tgz', '*.gz', '*.xz', '*.bz2', '*.tbz', '*.tbz2', '*.tar', '*.Z', '*.rar
    :return: List of files that are in compressed/zipped formats.
    """
    if verbose:
        print 'searching for compressed files, please wait...'
    if not file_type:
        extensions = ['*.zip', '*.tgz', '*.gz', '*.xz', '*.bz2', '*.tbz', '*.tbz2', '*.tar', '*.Z', '*.rar']
    else:
        extensions = [file_type]
    path = os.getcwd()
    result = []
    path, dirs, files = os.walk(path).next()
    try:
        for ext in extensions:
            for root, dirs, files in os.walk(path):
                for name in files:
                    if fnmatch.fnmatch(name, ext):
                        result.append(os.path.join(root, name))
        list.sort(result)
        return result

    except KeyboardInterrupt:
        print "\nSearch stopped, exiting unzipme.py"
        exit(0)

def get_extract_command():
    return

def extract_file(cur_file, zip_pass=False, verbose=False):
    """Extracts current file in sub-folder EXTRACTED

    :param cur_file:
    :return:
    """
    cwd = os.getcwd()
    extract_path = '{}/EXTRACTED/'.format(cwd)

    # TODO Finish *.rar format for extraction
    patterns = ['.zip', '.tgz', '.gz', '.xz', '.bz2', '.tbz', '.tbz2', '.tar', '.Z', '.rar', '.7z']
    if verbose:
        print "current file extracting: {}".format(os.path.basename(cur_file))
    try:
        # *.zip File extraction
        if cur_file.endswith(patterns[0]) and not zip_pass:
            try:
                zip_ref = zipfile.ZipFile(cur_file, 'r')
                zip_ref.extractall(extract_path)
                zip_ref.close()
                return
            except RuntimeError, err:
                answer = raw_input("\n'{}': Password invalid or missing, continue? (Y/N) : ".format(os.path.basename(cur_file)))
                if answer.lower() == 'y':
                    zip_pass = getpass.getpass(prompt='Enter Password: ')
                    print ''
                    extract_file(cur_file, zip_pass)
                else:
                    print "File '{}' could not be extracted\n".format(os.path.basename(cur_file))
                    return
            except AttributeError, err:
                print '{} : {}'.format(cur_file, err)
                exit(1)

        # *.zip File extraction w/ password
        elif cur_file.endswith(patterns[0]) and zip_pass:
            try:
                zip_ref = zipfile.ZipFile(cur_file, 'r')
                zip_ref.extractall(path=extract_path, pwd=zip_pass)
                zip_ref.close()
                return
            except RuntimeError, err:
                answer = raw_input("\nPassword invalid or missing, continue? (Y/N) : ")
                if answer.lower() == 'y':
                    zip_pass = getpass.getpass(prompt='Enter Password: ')
                    extract_file(cur_file, zip_pass)
                else:
                    print "File '{}' could not be extracted\n".format(os.path.basename(cur_file))
                    return
            except AttributeError, err:
                print '{} : {}'.format(cur_file, err)
                print "Exiting unzipme "
                exit(1)

        # *.tgz file extraction
        elif cur_file.endswith(patterns[1]):
            command = 'tar xf {} -C {}'.format(cur_file, extract_path)

            if os.path.isdir(extract_path):
                subprocess.call(command, shell=True, stdout=open(os.devnull, 'wb'))
                return
            else:
                os.mkdir(extract_path)
                os.chmod(extract_path, 0774)
                subprocess.call(command, shell=True, stdout=open(os.devnull, 'wb'))
                return

        # *.gz file extraction
        elif cur_file.endswith(patterns[2]):
            command = 'tar xf {} --directory {}'.format(cur_file, extract_path)

            if os.path.isdir(extract_path):
                subprocess.call(command, shell=True, stdout=open(os.devnull, 'wb'))
                return
            else:
                os.mkdir(extract_path)
                os.chmod(extract_path, 0774)
                subprocess.call(command, shell=True, stdout=open(os.devnull, 'wb'))
                return

        # *.xz file extraction
        elif cur_file.endswith(patterns[3]):
            command = 'unxz {}'.format(cur_file)
            if os.path.isdir(extract_path):
                os.chmod(extract_path, 0774)
                subprocess.call(command, shell=True, stdout=open(os.devnull, 'wb'))
                tar_file = os.path.splitext(cur_file)[0] + ''
                extract_file(tar_file)
                return
            else:
                os.mkdir(extract_path)
                os.chmod(extract_path, 0774)
                subprocess.call(command, shell=True, stdout=open(os.devnull, 'wb'))
                tar_file = os.path.splitext(cur_file)[0] + ''
                extract_file(tar_file)
                return

        # *.bz2 or *.tbz extraction
        elif cur_file.endswith(patterns[4]) or cur_file.endswith(patterns[5]) or cur_file.endswith(patterns[6]):
            command = 'tar -jxf {} --directory {}'.format(cur_file, extract_path)

            if os.path.isdir(extract_path):
                subprocess.call(command, shell=True, stdout=open(os.devnull, 'wb'))
                return
            else:
                os.mkdir(extract_path)
                os.chmod(extract_path, 0774)
                subprocess.call(command, shell=True, stdout=open(os.devnull, 'wb'))
                return

        # *.tar extract
        elif cur_file.endswith(patterns[7]):
            command = 'tar -xf {} -C {}'.format(cur_file, extract_path)
            if os.path.isdir(extract_path):
                subprocess.call(command, shell=True, stdout=open(os.devnull, 'wb'))
                return
            else:
                os.mkdir(extract_path)
                os.chmod(extract_path, 0774)
                subprocess.call(command, shell=True, stdout=open(os.devnull, 'wb'))
                return

        # *.Z file extraction
        elif cur_file.endswith(patterns[8]):
            command = 'uncompress {}'.format(cur_file)
            if os.path.isdir(extract_path):
                subprocess.call(command, shell=True, stdout=open(os.devnull, 'wb'))
            else:
                os.mkdir(extract_path)
                os.chmod(extract_path, 0774)
                subprocess.call(command, shell=True, stdout=open(os.devnull, 'wb'))
            return

        # *.rar or *.7z file extraction
        elif cur_file.endswith(patterns[9]) or cur_file.endswith(patterns[10]):
            command = '7z x {} -o{}'.format(cur_file, extract_path)
            if os.path.isdir(extract_path):
                subprocess.call(command, shell=True, stdout=open(os.devnull, 'wb'))
                return
            else:
                os.mkdir(extract_path)
                os.chmod(extract_path, 0774)
                subprocess.call(command, shell=True, stdout=open(os.devnull, 'wb'))
                return
        else:
            return


    except KeyError, err:
        print '{} : {}'.format(cur_file, err)
        print "Exiting unzipme"
        exit(1)

    except IOError, err:
        print '{} : {}'.format(cur_file, err)
        print "Exiting unzipme"
        exit(1)

    except KeyboardInterrupt:
        print "\nExiting unzipme.py"
        exit(0)


def set_extract_permisions(verbose=False):
    """Sets all sub file permissions to 777 in ./EXTRACTED

    :return:
    """
    if verbose:
        print 'setting file permissions, please wait...'
    cwd = os.getcwd()
    extract_path = '{}/EXTRACTED'.format(cwd)
    try:
        command = 'chmod 777 -R {}'.format(extract_path)
        subprocess.call(command, shell=True, stdout=open(os.devnull, 'wb'))
        return

    except KeyboardInterrupt:
        print "\nExiting unzipme.py"
        exit(0)


if __name__ == '__main__':
    main()
