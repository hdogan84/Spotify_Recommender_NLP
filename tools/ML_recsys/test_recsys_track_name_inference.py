import pytest
import recsys_track_name_inference
from recsys_track_name_inference import get_recommendation_title
import pandas as pd
import subprocess


### Test the module with differents input arguments ###
# Test with correct input arguments
def test_module_simple_run():
    result = subprocess.run(['python3', 'recsys_track_name_inference.py', '3', '5'], capture_output=True, text=True)
    assert result.returncode == 0

def test_module_invalid_fold_number():
    result = subprocess.run(['python3', 'recsys_track_name_inference.py', '-100', '5'], capture_output=True, text=True)
    assert result.returncode == 1

def test_module_invalid_transaction_id():
    result = subprocess.run(['python3', 'recsys_track_name_inference.py', '1', '-5'], capture_output=True, text=True)
    assert result.returncode == 1

def test_module_insufficient_input_args():
    result = subprocess.run(['python3', 'recsys_track_name_inference.py', '4'], capture_output=True, text=True)
    assert result.returncode == 1

### Test the standolone function ### 
def test_get_recommendation_return_type():
    ## Test the return variable type for a random input 
    assert type(get_recommendation_title("song and rain"))==pd.DataFrame

def test_get_recommendation_input_types():
    ## Test that input track name cannot be an empty string or none
    with pytest.raises(Exception):
        get_recommendation_title("")
    
    with pytest.raises(Exception):
        get_recommendation_title()

def test_get_recommendation_input_num():
    ## Test that input track name cannot be numeric variable
    with pytest.raises(Exception):
        get_recommendation_title(5)
    
    with pytest.raises(Exception):
        get_recommendation_title(2.3)