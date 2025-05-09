import unittest
from yaw.core.BashRunner import BashRunner
from pathlib import Path
class TestBashRunner(unittest.TestCase):

    def setUp(self):
        # Initialize any necessary objects or state before each test
        self.test_dir = "$HOME/yaw_test_dir"
        
    def test_initialization(self):
        # Test the initialization of the BashRunner
        runner = BashRunner(type="BashRunner", bash_cmd="ls", rundir=self.test_dir)
        self.assertIsInstance(runner, BashRunner)
        self.assertEqual(runner.runner_result, 0)
        self.assertEqual(runner.runner_status, "READY")
        # Inovked path must be false -> rundir is set
        self.assertEqual(runner.invoked_path, False)

    def test_required_param_missing(self):
        try:
            runner = BashRunner(type="BashRunner", rundir=self.test_dir)
            self.assertEqual(1, 2)
        except Exception as e:
            self.assertEqual(str(e), "Required argument(s) bash_cmd not found")
            
    def test_bad_param_set(self):
        # TODO: Add exception for this!
        try:
            runner = BashRunner(type = "BashRunner", bash_cmd = "ls",
                                rundir = self.test_dir, invent = 1)
            raise Exception("Exception no thrown")
        except Exception as e:
            self.assertEqual(str(e), "Invalid parameter(s) invent")

    def test_run_simple_ls(self):
        params = {
            "type": "BashRunner", "recipie_name": "yaw-test",
            "bash_cmd": "ls", "overwrite" : True,
            "rundir" : self.test_dir
        }
        runner = BashRunner(**params)
        runner.manage_parameters()
        runner.run()
        # Check yaw_wrapper exists
        # Check env.log exists
        
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
        pass
    
    def fill_rundir_files(self):
        pass

    def tearDown(self):
        # Auto delete self.test_dir if everything was OK. 
        pass

if __name__ == '__main__':
    print("Running tests for AbstractRunner...")
    unittest.main()