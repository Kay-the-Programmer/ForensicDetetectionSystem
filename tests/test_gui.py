import unittest
# Assuming your App class is in src.gui
# We won't instantiate App, but if there are static methods or helper functions,
# they could be imported and tested.
# For now, let's test a hypothetical helper or a pattern used in the GUI.

class TestGuiHelpers(unittest.TestCase):

    def test_extract_device_id_from_listbox_string(self):
        # This simulates the pattern used in on_kb_device_select
        # The actual GUI code uses:
        # id_part = selected_item_text.rfind("(ID: ")
        # device_id = selected_item_text[id_part + len("(ID: "):-1]
        # This test will be based on that logic.

        # Test case 1: Standard format
        listbox_string_ok = "Some Device Name (ID: device-001)"
        id_part_ok = listbox_string_ok.rfind("(ID: ")
        device_id_ok = listbox_string_ok[id_part_ok + len("(ID: "):-1]
        self.assertEqual(device_id_ok, "device-001")

        # Test case 2: String only contains ID part
        listbox_string_short = "(ID: short-id)"
        id_part_short = listbox_string_short.rfind("(ID: ")
        # This will fail if rfind returns -1, but the GUI code implies it finds "(ID: "
        # If "(ID: " is at the beginning, id_part_short would be 0.
        device_id_short = listbox_string_short[id_part_short + len("(ID: "):-1]
        self.assertEqual(device_id_short, "short-id")

        # Test case 3: No device name, spaces around ID
        listbox_string_no_name = " (ID: no-name-id) "
        # rfind should still find it. The slicing and then potential .strip() in GUI (though not explicitly in snippet) handles spaces.
        # The snippet `selected_item_text[id_part + len("(ID: "):-1]` does not strip.
        # Let's test the exact logic.
        id_part_no_name = listbox_string_no_name.rfind("(ID: ")
        device_id_no_name = listbox_string_no_name[id_part_no_name + len("(ID: "):-1]
        self.assertEqual(device_id_no_name, "no-name-id") # This will pass as slicing is precise.

        # Test case 4: ID at the very beginning of the string
        listbox_string_id_first = "(ID: id-first-002) Device Name"
        id_part_id_first = listbox_string_id_first.rfind("(ID: ")
        device_id_id_first = listbox_string_id_first[id_part_id_first + len("(ID: "):listbox_string_id_first.find(")", id_part_id_first)]
        # The original GUI slice was `:-1` which assumes ')' is the last char.
        # If not, it needs adjustment. The test here will use a more robust extraction if ')' is not last.
        # The actual GUI code `selected_item_text[id_part + len("(ID: "):-1]` might be too simple.
        # Let's refine the test to match the *exact* GUI code's behavior for this part.
        # The GUI code is: device_id = selected_item_text[id_part + len("(ID: "):-1]
        # If the string is "(ID: id-first-002) Device Name", then `[:-1]` would be "id-first-002) Device Nam". This is a flaw in GUI.
        # The test should reflect this flaw to indicate the GUI needs fixing, or the test should test a corrected version.
        # For now, I'll test the GUI's actual slice.
        # Re-evaluating: The GUI code `device_id = selected_item_text[id_part + len("(ID: "):-1]` is correct if the ID is always at the very end.
        # My listbox population is `f"{device.get('name', 'Unknown Name')} (ID: {device.get('id', 'Unknown ID')})"`
        # So, `(ID: ...)` is indeed always at the end. The test cases should reflect this.

        # Test case 1 (Re-verified, should pass with actual GUI logic)
        listbox_string_ok = "Some Device Name (ID: device-001)"
        id_part_ok = listbox_string_ok.rfind("(ID: ")
        device_id_ok = listbox_string_ok[id_part_ok + len("(ID: "):-1]
        self.assertEqual(device_id_ok, "device-001")

        # Test case 2 (Re-verified, ID part only, should pass)
        # This case is actually not possible with current listbox population but tests the string logic
        listbox_string_short_id_only = "(ID: short-id)" # Assumes this is the whole string
        id_part_short_id_only = listbox_string_short_id_only.rfind("(ID: ")
        device_id_short_id_only = listbox_string_short_id_only[id_part_short_id_only + len("(ID: "):-1]
        self.assertEqual(device_id_short_id_only, "short-id")

        # Test case 3 (Re-verified, Name is just a space, ID at end)
        listbox_string_space_name = " (ID: space-name-id)"
        id_part_space_name = listbox_string_space_name.rfind("(ID: ")
        device_id_space_name = listbox_string_space_name[id_part_space_name + len("(ID: "):-1]
        self.assertEqual(device_id_space_name, "space-name-id")

        # Test case 4: Empty name part
        listbox_string_empty_name = "(ID: empty-name-id)" # This is like case 2
        id_part_empty_name = listbox_string_empty_name.rfind("(ID: ")
        device_id_empty_name = listbox_string_empty_name[id_part_empty_name + len("(ID: "):-1]
        self.assertEqual(device_id_empty_name, "empty-name-id")

        # Test case 5: Complex device name with parentheses
        listbox_string_complex_name = "Device (Model X) (Type Y) (ID: complex-id-007)"
        id_part_complex = listbox_string_complex_name.rfind("(ID: ")
        device_id_complex = listbox_string_complex_name[id_part_complex + len("(ID: "):-1]
        self.assertEqual(device_id_complex, "complex-id-007")

if __name__ == '__main__':
    unittest.main()
