import yaml

from hootingyard.index.refine_index import refine_show
from test_hootingyard.refinement_test_data import get_refinement_test_data

def do_yaml_test(test_number:int):
    assert refine_show(**get_refinement_test_data(test_number,"input")) == get_refinement_test_data(test_number,"expected")

def test_refine1():
    do_yaml_test(1)

def test_refine2():
    do_yaml_test(2)

def test_refine3():
    do_yaml_test(3)

def test_refine4():
    do_yaml_test(4)



