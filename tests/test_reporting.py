import unittest
import os
import json
import shutil
from datetime import datetime
from src import reporting # Ensure this import works based on project structure

# Define a temporary directory for reports generated during tests
TEMP_REPORTS_DIR = "temp_test_reports"

class TestReporting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure the main forensic_reports directory for the module exists
        # as the reporting module might try to create it if it doesn't.
        # The tests themselves will use TEMP_REPORTS_DIR.
        if not os.path.exists(reporting.FORENSIC_REPORTS_DIR):
            os.makedirs(reporting.FORENSIC_REPORTS_DIR)

        # Create a temporary directory for test reports
        if os.path.exists(TEMP_REPORTS_DIR):
            shutil.rmtree(TEMP_REPORTS_DIR)
        os.makedirs(TEMP_REPORTS_DIR)
        # Override the reporting module's directory for the duration of the tests
        cls.original_reports_dir = reporting.FORENSIC_REPORTS_DIR
        reporting.FORENSIC_REPORTS_DIR = TEMP_REPORTS_DIR

    @classmethod
    def tearDownClass(cls):
        # Clean up the temporary directory
        if os.path.exists(TEMP_REPORTS_DIR):
            shutil.rmtree(TEMP_REPORTS_DIR)
        # Restore the original reports directory
        reporting.FORENSIC_REPORTS_DIR = cls.original_reports_dir

    def _common_report_data(self):
        return {
            "case_name": "Test Video Case",
            "investigator": "Test Investigator",
            "device_info": {"id": "test_device_001", "name": "CameraX"},
            "acquisition_details": [
                {"source_type": "video_file", "timestamp": datetime.now().isoformat(), "file_path": "/mnt/data/video.mp4"}
            ],
            "analysis_results": { # Existing analysis results (e.g., log, config)
                "log_analysis": {"total_entries": 100},
                "config_analysis": {"sensor_count": 5}
            },
            "notes": "This is a test report."
        }

    def test_generate_report_with_video_results(self):
        data = self._common_report_data()
        video_results = {
            "video_filename": "video.mp4",
            "duration": 120.5,
            "detected_objects_count": 15,
            "significant_events": [
                {"timestamp": "00:01:30", "description": "Object entered frame"},
                {"timestamp": "00:05:00", "description": "Suspicious activity detected"}
            ]
        }
        # Pass video_analysis_results directly in the call to generate_report
        report_path_txt = reporting.generate_report(**data, video_analysis_results=video_results)
        report_path_json = report_path_txt.replace(".txt", ".json")

        self.assertTrue(os.path.exists(report_path_txt))
        self.assertTrue(os.path.exists(report_path_json))

        # Verify text report content
        with open(report_path_txt, 'r') as f:
            txt_content = f.read()
        self.assertIn("VIDEO ANALYSIS FINDINGS", txt_content)
        self.assertIn("Video Filename: video.mp4", txt_content)
        self.assertIn("Video Duration: 120.5 seconds", txt_content)
        self.assertIn("Detected Objects Count: 15", txt_content)
        self.assertIn("- [00:01:30] Object entered frame", txt_content)

        # Verify JSON report content
        with open(report_path_json, 'r') as f:
            json_content = json.load(f)
        self.assertIn("video_analysis_results", json_content)
        self.assertEqual(json_content["video_analysis_results"]["video_filename"], "video.mp4")
        self.assertEqual(json_content["video_analysis_results"]["detected_objects_count"], 15)

    def test_generate_report_without_video_results(self):
        data = self._common_report_data()
        # video_analysis_results is explicitly not set or set to None (default for generate_report)

        report_path_txt = reporting.generate_report(**data) # video_analysis_results will be None by default
        report_path_json = report_path_txt.replace(".txt", ".json")

        self.assertTrue(os.path.exists(report_path_txt))
        self.assertTrue(os.path.exists(report_path_json))

        with open(report_path_txt, 'r') as f:
            txt_content = f.read()
        self.assertIn("VIDEO ANALYSIS FINDINGS", txt_content)
        self.assertIn("No video analysis results available.", txt_content)

        with open(report_path_json, 'r') as f:
            json_content = json.load(f)
        # In reporting.py, it's set to an empty dict if None
        self.assertEqual(json_content["video_analysis_results"], {})


    def test_generate_report_with_empty_video_results(self):
        data = self._common_report_data()
        # Pass an empty dictionary for video_analysis_results
        report_path_txt = reporting.generate_report(**data, video_analysis_results={})
        report_path_json = report_path_txt.replace(".txt", ".json")

        self.assertTrue(os.path.exists(report_path_txt))
        self.assertTrue(os.path.exists(report_path_json))

        with open(report_path_txt, 'r') as f:
            txt_content = f.read()
        self.assertIn("VIDEO ANALYSIS FINDINGS", txt_content)
        # Based on reporting.py logic, if video_analysis_results is an empty dict, it's treated as "not provided"
        self.assertIn("No video analysis results available.", txt_content)

        with open(report_path_json, 'r') as f:
            json_content = json.load(f)
        self.assertEqual(json_content["video_analysis_results"], {})

if __name__ == '__main__':
    unittest.main()
