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
    progress()


def parse_args():
    """Parses optional args and shows menu. 

    :return: args passed from command line.
    """
    parser = argparse.ArgumentParser(
        description='********** Finds compressed files and extracts them to ./EXTRACTED **********\n\n'
                    'Supports: *.zip, *.tgz, *.gz, *.xz, *.bz2, *.tbz, *.tbz2, *.tar, *.Z, *.rar')

    #Optional Arguments
    parser.add_argument("-v", "--verbose", help="Increase output verbosity. Default: False",
                        action="store_true")
    args = parser.parse_args()
    return args

def progress():
    """Displays progress of compressed files found and extracted

    """
    bundle_list = find_files_in_folder()
    bundle_length = len(bundle_list)
    if bundle_length > 1 and not bundle_length < 0:
        print "{} files found please wait...".format(bundle_length)
        set_file_permissions(bundle_list)
        pbar = progressbar.ProgressBar(
            widgets=[progressbar.Percentage(), ' ', progressbar.SimpleProgress(), progressbar.Bar()])
        for n in pbar(range(bundle_length)):
            extract_file(bundle_list[n])
            time.sleep(.2)

    elif bundle_length == 1:
        print "{} file found please wait...".format(bundle_length)
        set_file_permissions(bundle_list)
        if extract_file(bundle_list[0]):
            print "File '{}' extracted".format(os.path.basename(bundle_list[0]))
            exit(0)
        else:
            print "File '{}' could not be extracted".format(os.path.basename(bundle_list[0]))
            exit(0)
    else:
        print 'no compressed files found'
        exit(0)


def set_file_permissions(bundle_list):
    """Checks and sets permissions to compressed/zipped file.
    """
    for i in bundle_list:
        os.chmod(i, 0777)
    return


def find_files_in_folder():
    """Finds compressed files in directory, returns them as a list.

    SUPPORTED FORMATS: *.zip, *.tgz, *.gz, *.xz
    :return: List of files that are in compressed/zipped formats.
    """
    print 'searching for compressed files, please wait...'
    extensions = ['*.zip', '*.tgz', '*.gz', '*.xz', '*.bz2', '*.tbz', '*.tbz2', '*.tar', '*.Z', '*.rar']
    path = os.getcwd()
    result = []
    path, dirs, files = os.walk(path).next()
    file_count = len(files)
    pbar = progressbar.ProgressBar(
        widgets=[progressbar.Percentage(), ' ', progressbar.SimpleProgress(), progressbar.Bar()])
    try:
        for n in pbar(range(file_count)):
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


def extract_file(cur_file, zip_pass=False):
    """Extracts current file in sub-folder EXTRACTED

    :param cur_file:
    :return:
    """
    cwd = os.getcwd()
    extract_path = '{}/EXTRACTED/'.format(cwd)

    # TODO Finish *.rar format for extraction
    patterns = ['.zip', '.tgz', '.gz', '.xz', '.bz2', '.tbz', '.tbz2', '.tar', '.Z', '.rar', '.7z']

    try:
        # *.zip File extraction
        if cur_file.endswith(patterns[0]) and not zip_pass:
            try:
                zip_ref = zipfile.ZipFile(cur_file, 'r')
                zip_ref.extractall(extract_path)
                zip_ref.close()
                return True
            except RuntimeError, err:
                answer = raw_input("Password invalid or missing, continue? (Y/N) : ")
                if answer.lower() == 'y':
                    zip_pass = getpass.getpass(prompt='Enter Password: ')
                    extract_file(cur_file, zip_pass)
                else:
                    return False
            except AttributeError, err:
                print '{} : {}'.format(cur_file, err)
                exit(1)

        # *.zip File extraction w/ password
        if cur_file.endswith(patterns[0]) and zip_pass:
            try:
                zip_ref = zipfile.ZipFile(cur_file, 'r')
                zip_ref.extractall(path=extract_path, pwd=zip_pass)
                zip_ref.close()
                return True
            except RuntimeError, err:
                answer = raw_input("Password invalid or missing, continue? (Y/N) : ")
                if answer.lower() == 'y':
                    zip_pass = getpass.getpass(prompt='Enter Password: ')
                    extract_file(cur_file, zip_pass)
                else:
                    return False
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
            # print 'pattern xz: '.format(os.path.splitext(cur_file)[1])
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
            command = '7z x {} -o {}'.format(cur_file, extract_path)
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


def set_extract_permisions():
    """Sets all sub file permissions to 777 in ./EXTRACTED

    :return:
    """
    cwd = os.getcwd()
    extract_path = '{}/EXTRACTED/'.format(cwd)

    try:
        command = 'chmod 777 -R * {}'.format(extract_path)
        subprocess.call(command, shell=True, stdout=open(os.devnull, 'wb'))
        return

    except KeyboardInterrupt:
        print "\nExiting unzipme.py"
        exit(0)

if __name__ == '__main__':
    main()
