import json
import unittest

from tools.analyze_target_transport import intervals, mock_response, score


class AnalysisTests(unittest.TestCase):
    def test_parser_rejects_invalid_content(self):
        def response(content, finish="stop"):
            return json.dumps({"choices": [{"finish_reason": finish,
                                           "message": {"content": content}}]}).encode()
        self.assertEqual(score(response(' \n{"activate":0}\t')), (0, "valid"))
        self.assertEqual(score(mock_response(1)), (1, "valid"))
        for value in ('{"activate":{"activate":1}}', '{"activate":true}', '{"activate":null}', '{"activate":1.0}', '{"activate":"1"}',
                      '{"activate":1,"activate":1}', '1', '{"activate":1} done',
                      '```json\n{"activate":1}\n```'):
            self.assertIsNone(score(response(value))[0], value)
        self.assertIsNone(score(response('{"activate":1}', "length"))[0])
        self.assertEqual(score(b"\xff"), (None, "invalid_utf8"))

    def test_known_stratified_variance(self):
        groups = [[0]*16 for _ in range(8)]
        self.assertIsNone(intervals(groups)["interval_t"])
        groups[0][0] = 1
        result = intervals(groups)
        self.assertEqual((result["delta"], result["se"], result["welch_df"]), (1/128, 1/128, 15))
        self.assertAlmostEqual(result["interval_t"][1], (1+2.131449545559323)/128, places=10)
