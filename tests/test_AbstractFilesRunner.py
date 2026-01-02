from unittest import TestCase
from unittest.mock import patch

from yaw.core.AbstractFilesRunner import AbstractFilesRunner
from utils.logger import MyLogger, LoggerLevels

from pathlib import Path
import tempfile
import tarfile


class ConcreteRunner(AbstractFilesRunner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self):
        print("Testing...")


class TestAbstractRunner(TestCase):
    MyLogger.set_verbose_level(LoggerLevels.DEBUG)

    def test_clone_repo(self):
        # Ensure git clone string is constructed and executed
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            runner = ConcreteRunner(type="FilesRunner", recipie_name="t1",
                                    rundir=td_path, git_repo="https://example/repo.git",
                                    git_branch="mybranch",  create_dir=False)
            with patch("yaw.core.AbstractFilesRunner.BashCmd.run") as mock_run:
                runner.manage_parameters()
                mock_run.assert_called_once()
                cmd_called = mock_run.call_args[0][0]
                self.assertIn("git clone", cmd_called)
                self.assertIn("https://example/repo.git", cmd_called)
                self.assertIn("-b mybranch", cmd_called)

        # Branch without repo should raise on check
        runner_bad = ConcreteRunner(type="FilesRunner", recipie_name="t2",
                                    rundir=td_path, git_branch="no_repo_branch")
        with self.assertRaises(Exception):
            runner_bad.check_parameters()

    def test_reference_rundir(self):
        # Create source folder with a small and a big file and verify copying and symlink behavior
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as dest:
            src_p = Path(src)
            dest_p = Path(dest)
            # small file
            small = src_p / "small.txt"
            small.write_text("hello")
            # big file ( > 2MB threshold in util )
            big = src_p / "big.bin"
            with open(big, "wb") as fd:
                fd.write(b"0" * (2 * 1024 * 1024 + 10))

            runner = ConcreteRunner(type="FilesRunner", recipie_name="t_ref",
                                    rundir=dest_p, ref_rundir={src_p}, create_dir=False)
            runner.manage_parameters()

            self.assertTrue((dest_p / "small.txt").exists())
            self.assertFalse((dest_p / "small.txt").is_symlink())
            self.assertTrue((dest_p / "big.bin").exists())
            self.assertTrue((dest_p / "big.bin").is_symlink())

    def test_rundir_files(self):
        # Create a file and ensure it's copied to rundir
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as src:
            td_p = Path(td)
            src_p = Path(src)
            f = src_p / "copyme.txt"
            f.write_text("copycontent")

            runner = ConcreteRunner(type="FilesRunner", recipie_name="t_files",
                                    rundir=td_p, rundir_files={f}, create_dir=False)
            runner.manage_parameters()

            dest_f = td_p / "copyme.txt"
            self.assertTrue(dest_f.exists())
            self.assertEqual(dest_f.read_text(), "copycontent")

    def test_targz_files(self):
        # Create a tar.gz archive and ensure files are extracted into rundir
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as src:
            td_p = Path(td)
            src_p = Path(src)
            inner = src_p / "inside.txt"
            inner.write_text("inside")

            tar_path = src_p / "test.tar.gz"
            with tarfile.open(tar_path, "w:gz") as tar:
                tar.add(inner, arcname="inside.txt")

            runner = ConcreteRunner(type="FilesRunner", recipie_name="t_tgz",
                                    rundir=td_p, tar_gz_files={tar_path}, create_dir=False)
            runner.manage_parameters()

            extracted = td_p / "inside.txt"
            self.assertTrue(extracted.exists())
            self.assertEqual(extracted.read_text(), "inside")

    def test_manage_parameters(self):
        # Combine operations: clone (patched), copy files, extract tar
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as td:
            src_p = Path(src)
            td_p = Path(td)
            # file to copy
            f = src_p / "f.txt"
            f.write_text("1")
            # tar file
            inner = src_p / "inner.txt"
            inner.write_text("i")
            tar_path = src_p / "mix.tar.gz"
            with tarfile.open(tar_path, "w:gz") as tar:
                tar.add(inner, arcname="inner.txt")

            with patch("yaw.core.AbstractFilesRunner.BashCmd.run") as mock_run:
                runner = ConcreteRunner(type="FilesRunner", recipie_name="t_manage",
                                        create_dir=False,
                                        rundir=td_p, git_repo="https://ex.git",
                                        rundir_files={f}, tar_gz_files={tar_path})
                runner.manage_parameters()
                mock_run.assert_called_once()

            self.assertTrue((td_p / "f.txt").exists())
            self.assertTrue((td_p / "inner.txt").exists())
