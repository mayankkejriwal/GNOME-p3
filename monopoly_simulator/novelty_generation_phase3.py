from monopoly_simulator import novelty_generator_v2
from monopoly_simulator import novelty_functions_v2
#from monopoly_simulator.player import Player
#from monopoly_simulator.location import RealEstateLocation
import json
import numpy as np
import os
from inspect import signature
import random
#from test_harness_random_socket_v2_test import meta_seed
import ast

def set_depth(dep, tournament = None):
    global depth, class_list, func_list, arg_list, arg_print_dic
    # arg_print_dic: this is for the output, record both keys and values of arguments
    # arg_list: this is for simulator, contain values of arguments only
    depth = dep
    class_list = [str(0)]*depth
    func_list = [str(0)]*depth
    arg_list = [[] for _ in range(depth)]
    arg_print_dic = dict()
    if tournament ==1:
        class_list, func_list = ["SpatialRepresentationNovelty", "GranularityRepresentationNovelty",
                                 "GranularityRepresentationNovelty", "ContingentAttributeNovelty",
                                 "NumberClassNovelty"], ["global_reordering", "granularity_novelty1",
                                                         "granularity_novelty1", "auxiliary_go",
                                                         "card_novelty"]  ### Comment out for constant random novelty
    elif tournament==0:
        class_list, func_list =["RelationsNovelty", "GranularityRepresentationNovelty", "GranularityRepresentationNovelty",
                                "NumberClassNovelty", "GranularityRepresentationNovelty"],["change_tax_calc", "granularity_novelty1", "granularity_novelty1", "card_novelty", "granularity_novelty1"]


def constant_random_novelty(meta_seed, hierarchy = 'All'):
    # param hierarchy: the string that specify hierarchy. only support: ['All', 'Events', 'Environments'].
    if hierarchy not in ['All', 'Events', 'Environments']:
        raise('Please check parameter hierarchym, only support (All, Events, Environments), current: ' + str(hierarchy))

    global meta_seed_value
    meta_seed_value = meta_seed
    random.seed(meta_seed)
    with open('config.json') as f:
        novelty_schema = json.load(f)

    novelty_schema = novelty_schema[hierarchy]
    module_name = "novelty_generator_v2"
    for i in range(depth):
        class_name = str(random.choice(list(novelty_schema)))
        func_name = str(random.choice(list(novelty_schema[class_name])))

        class_list[i] = (class_name)
        func_list[i] = (func_name)

        #
        module = __import__(module_name)
        cls = getattr(module, class_name, None)
        instance = cls()
        func = getattr(instance, func_name)
        arg_set = list((str(signature(func)).strip("(").strip(")")).split(", "))
        print(class_name + "-->" + func_name)
        for argument in arg_set:
            # arg_value.append(current_gameboard) if argument=="current_gameboard" else arg_value.append(random.choice(novelty_schema[class_name][func_name][argument]))
            #
            if argument == "current_gameboard":
                arg_list[i].append('current_gameboard')
            else:
                arg = random.choice(novelty_schema[class_name][func_name][argument])
                arg_list[i].append(arg)
                if i in arg_print_dic:
                    arg_print_dic[i].append({argument: arg})
                else:
                    arg_print_dic[i] = [{argument: arg}]
        # only for random selection
        # to avoid duplicatically inject primitive (duplication will overwrite the function, making the expected depth)
        del novelty_schema[class_name][func_name]
        if not novelty_schema[class_name]:
            del novelty_schema[class_name]
        ##

def random_novelty_inject(current_gameboard, meta_seed):
    with open('config.json') as f:
        novelty_schema = json.load(f)
    module_name = "novelty_generator_v2"
    #class_list, func_list = ["SpatialRepresentationNovelty", "GranularityRepresentationNovelty",
    #                         "GranularityRepresentationNovelty", "ContingentAttributeNovelty",
    #                         "NumberClassNovelty"],["global_reordering", "granularity_novelty1",
    #                                                "granularity_novelty1", "auxiliary_go", "card_novelty"] ### Comment out for constant random novelty


    for i in range(depth):
        ''' Uncomment 1st 2 lines and comment out next 4 lines for constant random novelty'''
        class_name = class_list[i]
        func_name = func_list[i]
        arg_set = arg_list[i]
        #class_name = "RelationsNovelty"
        #func_name = "reassign_process_move_consequences"
        #class_list.append(class_name)
        #func_list.append(func_name)
        module = __import__(module_name)
        cls = getattr(module, class_name, None)
        instance = cls()
        func = getattr(instance, func_name)

        arg_value = []
        for argument in arg_set:
            # arg_value.append(current_gameboard) if argument=="current_gameboard" else arg_value.append(random.choice(novelty_schema[class_name][func_name][argument]))
            #
            if argument == "current_gameboard":
                arg_value.append(current_gameboard)
            else:
                arg_value.append(argument)
            #
        func(*arg_value)
    return class_list, func_list, arg_print_dic, meta_seed_value



def phase3_novelty_inject(current_gameboard, novelty_name):

    module_name = "novelty_generator_v2"
    novelty_name = novelty_name.lower()

    # read phase3_novelty_config
    with open('phase3_novelty_config.json') as f:
        novelty_list = json.load(f)
        novelty_schema = novelty_list[novelty_name]
        class_list = novelty_schema["class_list"]
        func_list = novelty_schema["func_list"]
        arg_list = novelty_schema["arg_list"]
    depth = len(class_list)

    #
    for i in range(depth):
        ''' Uncomment 1st 2 lines and comment out next 4 lines for constant random novelty'''
        class_name = class_list[i]
        func_name = func_list[i]
        #print(arg_list[i])
        #arg_set = arg_list[i].strip('][').split(', ')

        #"""
        #print(arg_list[i])
        arg_set = []
        for arg in arg_list[i]:
            #print('----')
            #print(arg)
            #print(type(arg))
            if isinstance(arg, int) or isinstance(arg, float):
                arg_set.append(arg)
            elif '[' in arg:
                #print(ast.literal_eval(arg))
                arg_set.append(str(arg).strip('][').split(', '))
            else:
                arg_set.append(arg)

        #print(arg_set)
        #print('------------')
        #"""
        #print(arg_set)
        #print(arg_set)
        #print(len(arg_set[1]))
        #class_name = "RelationsNovelty"
        #func_name = "reassign_process_move_consequences"
        #class_list.append(class_name)
        #func_list.append(func_name)
        module = __import__(module_name)
        cls = getattr(module, class_name, None)
        instance = cls()
        func = getattr(instance, func_name)

        arg_value = []
        for argument in arg_set:
            # arg_value.append(current_gameboard) if argument=="current_gameboard" else arg_value.append(random.choice(novelty_schema[class_name][func_name][argument]))
            #
            if argument == "current_gameboard":
                arg_value.append(current_gameboard)
            else:
                arg_value.append(argument)
            #
        #print(arg_value)
        func(*arg_value)
    return()




