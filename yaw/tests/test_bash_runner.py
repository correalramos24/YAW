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
        print("")
        params = {"recipie_name": "test_init",
                  "type":"BashRunner", 
                  "bash_cmd":"ls", 
                  "rundir":self.test_dir,
                  "verbose":True}
        runner = BashRunner(**params)
        self.assertIsInstance(runner, BashRunner)
        self.assertEqual(runner.runner_result, 0)
        self.assertEqual(runner.runner_status, "READY")
        # Inovked path must be false -> rundir is set
        self.assertEqual(runner.invoked_path, False)

    def test_derive_recipie(self):
        # Test the derive_recipie method
        print("")
        params = {"recipie_name": "test_derive",
                  "type":"BashRunner", 
                  "bash_cmd":"ls",
                  "args": ["-l", "-a"],
                  "rundir":self.test_dir,
                  "verbose":True}
        runner = BashRunner(**params)
        derived_list = runner.derive_recipies()
        

    def test_required_param_missing(self):
        try:
            runner = BashRunner(type="BashRunner", rundir=self.test_dir)
            self.assertEqual(1, 2)
        except Exception as e:
            self.assertEqual(str(e), "Required argument(s) bash_cmd not found")
            
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
            "type": "BashRunner", "recipie_name": "yaw-test",
            "bash_cmd": "ls",
            "rundir" : self.test_dir
        }
        runner = BashRunner(**params)
        try:
            runner.manage_parameters()
        except Exception as e:
            self.assertEqual(str(e), "Creating an already existing dir!")
        
    def test_clone_repo(self):
        params = {
            "type": "BashRunner", "recipie_name": "yaw-test",
            "bash_cmd": "git status",
            "rundir" : self.test_dir,
            "git_repo": ""
        }
    
    def fill_rundir_files(self):
        pass

    def tearDown(self):
        # Auto delete self.test_dir if everything was OK. 
        pass
    
if __name__ == '__main__':
    print("Running tests for BashRunner...")
    unittest.main()