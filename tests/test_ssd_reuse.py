import hashlib
import tempfile
import unittest
from pathlib import Path
from tools.reuse_ssd_assets import contained, data_destination, digest, verified_copy
from tools.enforce_ssd_data_only import check_snapshot


class AssetCopyTests(unittest.TestCase):
    def test_cleanup_rejects_unknown_and_modified_source_files(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            root, workspace = base/'ssd', base/'repo'
            workspace.mkdir()
            original = workspace/'main.py'
            original.write_text('print(1)')
            target = root/'runtime/source'
            target.mkdir(parents=True)
            copy = target/'main.py'
            copy.write_bytes(original.read_bytes())
            assets = [dict(source=str(original), relative_destination='runtime/source/main.py',
                           bytes=copy.stat().st_size, sha256=digest(copy))]
            self.assertEqual(check_snapshot(root, workspace, assets)[0], target.resolve())
            extra = target/'user_edits.py'
            extra.write_text('keep me')
            with self.assertRaises(ValueError):check_snapshot(root, workspace, assets)
            extra.unlink()
            copy.write_text('new edits')
            with self.assertRaises(ValueError):check_snapshot(root, workspace, assets)
            self.assertTrue(copy.exists())

    def test_ssd_policy_rejects_code_and_runtime_trees(self):
        root = Path.cwd()
        for name in ('weights/model.py', 'datasets/helper.ps1', 'runs/tool.exe',
                     'manifests/package.whl', 'runtime/source/README.md', '../escape.json'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                data_destination(root, name)
        for name in ('weights/model.gguf', 'datasets/tasks.jsonl', 'runs/results.csv',
                     'manifests/source.json'):
            self.assertEqual(data_destination(root, name), (root/name).resolve())

    def asset(self,root,data=b'checkpoint data'*2000):
        source=root/'source.bin'
        source.write_bytes(data)
        destination=root/'copy/source.bin'
        return dict(source=str(source),destination=str(destination),bytes=len(data),
                    expected_hash=hashlib.sha256(data).hexdigest(),expected_hash_algorithm='sha256')

    def test_copy_verifies_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);a=self.asset(root)
            result=verified_copy(a)
            self.assertEqual(result['status'],'copied_and_readback_verified')
            self.assertEqual(Path(a['source']).read_bytes(),Path(a['destination']).read_bytes())
            self.assertEqual(verified_copy(a)['status'],'already_present_verified')

    def test_wrong_source_digest_is_not_promoted(self):
        with tempfile.TemporaryDirectory() as folder:
            a=self.asset(Path(folder));a['expected_hash']='0'*64
            with self.assertRaises(ValueError):verified_copy(a)
            self.assertFalse(Path(a['destination']).exists())

    def test_existing_conflict_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);a=self.asset(root);dest=Path(a['destination'])
            dest.parent.mkdir();dest.write_bytes(b'user data')
            with self.assertRaises(ValueError):verified_copy(a)
            self.assertEqual(dest.read_bytes(),b'user data')

    def test_partial_resume_including_empty_partial(self):
        for offset in (0,100):
            with tempfile.TemporaryDirectory() as folder:
                root=Path(folder);a=self.asset(root);dest=Path(a['destination'])
                dest.parent.mkdir()
                partial=dest.with_name(dest.name+'.causalfade-import.partial')
                partial.write_bytes(Path(a['source']).read_bytes()[:offset])
                result=verified_copy(a)
                self.assertEqual(result['sha256'],a['expected_hash'])
                self.assertFalse(partial.exists())

    def test_invalid_partial_does_not_overwrite_or_continue(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);a=self.asset(root);dest=Path(a['destination'])
            dest.parent.mkdir();partial=dest.with_name(dest.name+'.causalfade-import.partial')
            partial.write_bytes(b'incorrect prefix')
            with self.assertRaises(ValueError):verified_copy(a)
            self.assertEqual(partial.read_bytes(),b'incorrect prefix')
            self.assertFalse(dest.exists())

    def test_git_blob_digest_and_path_containment(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);a=self.asset(root)
            data=Path(a['source']).read_bytes()
            self.assertEqual(digest(Path(a['source']),'git-blob-sha1'),hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest())
            with self.assertRaises(ValueError):contained(root,'../escape')
            with self.assertRaises(ValueError):contained(root,'.')


if __name__=='__main__':unittest.main()
