import unittest
from yaw.core.BashRunner import BashRunner
from yaw.utils import enable_info
from pathlib import Path
import shutil
import os
class TestBashRunner(unittest.TestCase):

    def setUp(self):
        # Initialize any necessary objects or state before each test
        self.test_dir = "$HOME/yaw_test_dir"
        
    def test_initialization(self):
        # Test the initialization of the BashRunner
        params = {"recipie_name": "test_init",
                  "type":"BashRunner", "bash_cmd":"ls", 
                  "rundir":self.test_dir,"verbose":True}
        runner = BashRunner(**params)
        self.assertIsInstance(runner, BashRunner)
        self.assertEqual(runner.runner_result, 0)
        self.assertEqual(runner.runner_status, "READY")
        # Inovked path must be false -> rundir is set
        self.assertEqual(runner.invoked_path, False)

    def test_simple_run(self):
        # Test a simple run of the BashRunner
        params = {"recipie_name": "test_simple_run",
                  "type":"BashRunner", "bash_cmd":"ls", 
                  "verbose":True}
        runner = BashRunner(**params)
        runner.manage_parameters()
        runner.run()
        self.assertEqual(runner.runner_status, "OK")
        self.assertTrue(Path("yaw_wrapper.sh").exists())
        self.assertTrue(Path("env.log").exists())

    def test_derive_recipie(self):
        params = {"recipie_name": "test_derive",
                  "type":"BashRunner", 
                  "bash_cmd":"ls", "create_dir":False,
                  "args": ["-l", "-a", "-lah"],
                  "rundir":self.test_dir,
                  "verbose":True}
        runner = BashRunner(**params)
        derived_list = runner.derive_recipies()
        
        for l in derived_list:
            l.manage_parameters()
            l.run()
        
    def test_required_param_missing(self):
        try:
            runner = BashRunner(
                recipie_name="test_missing_param",
                type="BashRunner",
                rundir=self.test_dir,
                verbose=True)
            self.assertEqual(1, 2)
        except Exception as e:
            self.assertEqual(str(e), "Not found req argument(s) bash_cmd")
            
    def test_bad_param_set(self):
        try:
            runner = BashRunner(type = "BashRunner", bash_cmd = "ls",
                                rundir = self.test_dir, invent = 1)
            raise Exception("Exception no thrown")
        except Exception as e:
            self.assertEqual(str(e), "Invalid parameter(s) invent")

    def test_run_simple_ls(self):
        print("")
        test_path = self.test_dir + "/test_run_simple_ls"
        params = {
            "type": "BashRunner", "recipie_name": "yaw-test-simple-ls",
            "bash_cmd": "ls", "overwrite" : True,
            "rundir" : test_path, "verbose":True
        }
        runner = BashRunner(**params)
        runner.manage_parameters()
        runner.run()
        test_path_obj = Path(os.path.expandvars(test_path))
        self.assertTrue(Path(test_path_obj, "yaw_wrapper.sh").exists())
        self.assertTrue(Path(test_path_obj, "env.log").exists())
        
    def test_no_overwrite_rundir(self):
        #overwrite is false by default
        params = {
            "type": "BashRunner", "recipie_name": "test_no_overwrite_rundir",
            "bash_cmd": "ls", "verbose": True, "rundir" : self.test_dir
        }
        runner = BashRunner(**params)
        try:
            runner.manage_parameters()
        except Exception as e:
            print("Exception caught:", str(e))
            self.assertEqual(str(e), "Creating an already existing dir!")
        
    
    def fill_rundir_files(self):
        pass

    def tearDown(self):
        # Auto delete self.test_dir if everything was OK. 
        pass
    
if __name__ == '__main__':
    print("Running tests for BashRunner...")
    unittest.main()