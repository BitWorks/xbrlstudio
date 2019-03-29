"""
:mod: 'BookRun'
~~~~~~~~~~~~~~~

..  py:module:: BookRun
    :copyright: Copyright BitWorks LLC, All rights reserved.
    :license: MIT
    :synopsis: Entry point to run XBRLStudio with the python 3 interpreter
    :description: To run the program, type the following at a command prompt:

    $ python BookRun.py

XBRLStudio1 direct dependencies:
    Python 3.6.1
    Arelle 1.0
        lxml 3.8.0
        isodate 0.5.4
    PyQt5 5.9
        PyQtChart
    Qt5 5.9
    sqlalchemy 1.1.11
"""

try:
    import sys, os, datetime, logging
    logger = logging.getLogger()
    from PyQt5 import QtWidgets
    import BookView, BookValidator
except Exception as err:
    logger.error("{0}:BookRun import error:".format(str(datetime.datetime.now()) + str(err)))

#module-level directories
Global_app_dir = os.path.getcwd() #base dir for program files
Global_tmp_dir = os.path.join(Global_app_dir, "tmp") #temporary files (e.g., *_fct.xml, *.pdf)
Global_log_dir = os.path.join(Global_app_dir, "log") #log files
Global_key_dir = os.path.join(Global_app_dir, "key") #keyfile folder (sale ID file and key file)

def ensureDirs(target_dirs):
    try:
        for dir in target_dirs:
            if not os.path.exists(dir):
                os.mkdir(dir)
        return True
    except Exception as err:
        logger.error("{0}:BookRun ensureDirs error:".format(str(datetime.datetime.now()) + str(err)))
        return False

def startupRegistrationCheck():
    global Global_key_dir
    try:
        registration_status = False
        startup_validator = BookValidator.BookValidator()
        sale_id = None
        id_path = os.path.join(Global_key_dir, "XBRLStudio1_SaleID.txt")
        kf_path = os.path.join(Global_key_dir, "XBRLStudio1_Key.txt")
        if os.path.isfile(id_path) and os.path.isfile(kf_path):
            sale_id_fh = open(os.path.join(Global_key_dir, "XBRLStudio1_SaleID.txt"), "r")
            sale_id = sale_id_fh.read()
            sale_id_fh.close()
            key_fh = open(os.path.join(Global_key_dir, "XBRLStudio1_Key.txt"), "r")
            input_key = key_fh.read()
            key_fh.close()
            expected_key = startup_validator.keygen(sale_id)
            if input_key == expected_key:
                registration_status = True
            else:
                registration_status = False
        else:
            registration_status = False
    except Exception as err:
        logger.error("{0}:BookRun startupRegistrationCheck error:".format(str(datetime.datetime.now()) + str(err)))

    return registration_status

def environmentSetup():
    global Global_app_dir
    global Global_tmp_dir
    global Global_log_dir
    global Global_key_dir
    try:
        target_dirs = [Global_app_dir,
                       Global_tmp_dir,
                       Global_log_dir,
                       Global_key_dir]
        directories = ensureDirs(target_dirs)
        registration = startupRegistrationCheck()
    except Exception as err:
        logger.error("{0}:BookRun environmentSetup error:".format(str(datetime.datetime.now()) + str(err)))

    return directories, registration

def main():
    global Global_app_dir
    global Global_tmp_dir
    global Global_log_dir
    global Global_key_dir
    try:
        directories, registration = environmentSetup()
        if directories is True:
            logger_fn = os.path.join(Global_log_dir, "XBRLStudio1.log")
            if os.path.isfile(logger_fn):
                logger_fn_size = os.path.getsize(logger_fn)
                if logger_fn_size > 10000:
                    os.remove(logger_fn)
            logger_fh = logging.FileHandler(logger_fn)
            logger_fh.setLevel(logging.INFO)
            logger.addHandler(logger_fh)
            logger.info("{0}:Initializing MainApplication".format(str(datetime.datetime.now())))
            app = QtWidgets.QApplication(sys.argv)
            bmw = BookView.BookMainWindow([Global_app_dir,
                                           Global_tmp_dir,
                                           Global_log_dir,
                                           Global_key_dir], registration)
            bmw.show()
            return_val = sys.exit(app.exec())
            logger.info("{0}:Exit_status={1}".format(str(datetime.datetime.now()), return_val))

            return return_val
        else:
            logger.error("{0}:Environment setup failed. '{1}' is not a supported platform.".format(str(datetime.datetime.now()), sys.platform))
    except Exception as err:
        logger.error("{0}:Main setup failed:{1}".format(str(datetime.datetime.now()), str(err)))

if __name__ == "__main__":
    main()
