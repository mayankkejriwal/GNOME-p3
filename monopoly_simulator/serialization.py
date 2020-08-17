import json
import numpy
from monopoly_simulator.player import Player
from monopoly_simulator.location import RealEstateLocation


def _prune_serialize_history(pruned_gameboard_serial_obj):
    del pruned_gameboard_serial_obj['bank']
    total_chance_card_names = list(pruned_gameboard_serial_obj['cards']['chance_cards'].keys())
    picked_chance_card_details = dict()
    for card in total_chance_card_names:
        if card in pruned_gameboard_serial_obj['cards']['picked_chance_cards']:   #nly retaining card details of picked cards
            picked_chance_card_details[card] = pruned_gameboard_serial_obj['cards']['chance_cards'][card]
    pruned_gameboard_serial_obj['cards']['picked_chance_card_details'] = picked_chance_card_details

    total_community_chest_card_names = list(pruned_gameboard_serial_obj['cards']['community_chest_cards'].keys())
    picked_cc_card_details = dict()
    for card in total_community_chest_card_names:
        if card in pruned_gameboard_serial_obj['cards']['picked_community_chest_cards']:   #nly retaining card details of picked cards
            picked_cc_card_details[card] = pruned_gameboard_serial_obj['cards']['community_chest_cards'][card]
    pruned_gameboard_serial_obj['cards']['picked_community_chest_card_details'] = picked_cc_card_details

    del pruned_gameboard_serial_obj['cards']['chance_cards']
    del pruned_gameboard_serial_obj['cards']['community_chest_cards']

    return pruned_gameboard_serial_obj


def _serialize_history(current_gameboard):
    history = list()
    for i in range(len(current_gameboard['history']['function'])):
        hist_dict = dict()
        func_name = current_gameboard['history']['function'][i].__name__
        hist_dict['function'] = func_name

        param_obj = current_gameboard['history']['param'][i]
        hist_dict['param'] = dict()

        for k, v in param_obj.items():
            if k == 'player':
                hist_dict['param'][k] = v.player_name
            elif k == 'allowable_moves':
                allowable_moves_list = list()
                for move in v:
                    allowable_moves_list.append(move.__name__)
                hist_dict['param'][k] = allowable_moves_list
            elif k == 'code':
                hist_dict['param'][k] = v
            elif k == 'asset':
                hist_dict['param'][k] = v.name
            elif k == 'self':
                if isinstance(v, Player):
                    hist_dict['param'][k] = v.player_name
                elif isinstance(v, RealEstateLocation):
                    hist_dict['param'][k] = v.name
            elif k == 'amount':
                hist_dict['param'][k] = float(v)
            elif k == 'current_gameboard':
                pass
            elif k == 'from_player':
                hist_dict['param'][k] = v.player_name
            elif k == 'to_player':
                hist_dict['param'][k] = v.player_name
            elif k == 'offer':
                hist_dict['param'][k] = dict()
                for k1, v1 in v.items():
                    if k1 == 'property_set_offered' or k1 == 'property_set_wanted':
                        hist_dict['param'][k][k1] = list()
                        for prop in v1:
                            hist_dict['param'][k][k1].append(prop.name)
                    elif k1 == 'cash_offered' or k1 == 'cash_wanted':
                        hist_dict['param'][k][k1] = float(v1)
            elif k == 'add_house':
                hist_dict['param'][k] = v
            elif k == 'add_hotel':
                hist_dict['param'][k] = v
            elif k == 'rel_move':
                hist_dict['param'][k] = int(v)
            elif k == 'new_position':
                hist_dict['param'][k] = int(v)
            elif k == 'check_for_go':
                hist_dict['param'][k] = v
            elif k == 'die_total':
                hist_dict['param'][k] = int(v)
            elif k == 'card':
                hist_dict['param'][k] = type(v).__name__
            elif k == 'current_bid':
                hist_dict['param'][k] = float(v)
            elif k == 'pack':
                hist_dict['param'][k] = v
            elif k == "starting_player_index":
                hist_dict['param'][k] = v
            elif k == 'die_objects' or k == 'choice':
                pass
            elif k == 'description':
                hist_dict['param'][k] = v
            else:
                print('This param object not included, key: ', k, " value: ", v, " function name: ", func_name)

        return_obj = current_gameboard['history']['return'][i]

        if return_obj is None:
            hist_dict['return'] = None
        elif isinstance(return_obj, int):
            hist_dict['return'] = int(return_obj)
        elif isinstance(return_obj, list):
            hist_dict['return'] = list()
            for i in return_obj:
                hist_dict['return'].append(int(i))
        elif isinstance(return_obj, float):
            hist_dict['return'] = float(return_obj)
        elif isinstance(return_obj, numpy.int64):
            hist_dict['return'] = int(return_obj)
        elif isinstance(return_obj, bool):
            hist_dict['return'] = return_obj
        elif isinstance(return_obj, tuple):
            hist_dict['return'] = dict()
            for item in return_obj:
                if isinstance(item, list):   # trade offer tuples contain 2 lists (for trade offers to multiple players)
                    function_list = list()
                    param_list = list()
                    for f in item:                             # --> one for the function, the other for params
                        if not isinstance(f, dict):
                            function_list.append(f.__name__)
                        else:
                            prm_dict = dict()
                            for k, v in f.items():
                                if k == 'from_player':
                                    prm_dict[k] = v.player_name
                                elif k == 'to_player':
                                    prm_dict[k] = v.player_name
                                elif k == 'offer':
                                    prm_dict[k] = dict()
                                    for k1, v1 in v.items():
                                        if k1 == 'property_set_offered' or k1 == 'property_set_wanted':
                                            prm_dict[k][k1] = list()
                                            for prop in v1:
                                                prm_dict[k][k1].append(prop.name)
                                        elif k1 == 'cash_offered' or k1 == 'cash_wanted':
                                            prm_dict[k][k1] = float(v1)
                            param_list.append(prm_dict)
                    hist_dict['return']['function'] = function_list
                    hist_dict['return']['param'] = param_list
                elif not isinstance(item, dict):
                    hist_dict['return']['function'] = item.__name__
                elif isinstance(item, dict):
                    hist_dict['return']['param'] = dict()
                    for k, v in item.items():
                        if k == 'player':
                            hist_dict['return']['param'][k] = v.player_name
                        elif k == 'asset':
                            hist_dict['return']['param'][k] = v.name
                        elif k == 'code':
                            hist_dict['return']['param'][k] = v

                else:
                    print("This return val not included in return history")
        else:
            print("This return val not included in return history: ", return_obj, type(return_obj))

        history.append(hist_dict)
    return history


def serialize_gameboard(current_gameboard):
    history_serial_obj = _serialize_history(current_gameboard)
    current_gameboard_serial_obj = dict()
    bank_serial_obj = current_gameboard['bank'].serialize()
    players_serial_obj = dict()
    for player in current_gameboard['players']:
        players_serial_obj[player.player_name] = player.serialize()

    card_serial_obj = dict()
    card_serial_obj['chance_cards'] = dict()
    card_serial_obj['community_chest_cards'] = dict()
    for card in current_gameboard['chance_cards']:
        card_serial_obj['chance_cards'][card.name] = card.serialize()
    for card in current_gameboard['community_chest_cards']:
        card_serial_obj['community_chest_cards'][card.name] = card.serialize()

    location_serial_obj = dict()
    location_sequence_list = list()
    set_location_seq = set()
    for loc in current_gameboard['location_sequence']:
        set_location_seq.add(loc)
        location_sequence_list.append(loc.name)
    for loc in set_location_seq:
        location_serial_obj[loc.name] = loc.serialize()

    picked_chance_cards_list = list()
    for card in current_gameboard['picked_chance_cards']:
        picked_chance_cards_list.append(card.name)

    picked_community_chest_cards_list = list()
    for card in current_gameboard['picked_community_chest_cards']:
        picked_community_chest_cards_list.append(card.name)

    total_die_seq = list()
    num_dies = len(current_gameboard['die_sequence'])
    die_rolls = len(current_gameboard['die_sequence'][0])
    for i in range(die_rolls):
        die_seq = list()
        for j in range(num_dies):
            die_seq.append(int(current_gameboard['die_sequence'][j][i]))
        total_die_seq.append(die_seq)

    current_gameboard_serial_obj['bank'] = bank_serial_obj
    current_gameboard_serial_obj['players'] = players_serial_obj
    current_gameboard_serial_obj['cards'] = card_serial_obj
    current_gameboard_serial_obj['cards']['picked_chance_cards'] = picked_chance_cards_list
    current_gameboard_serial_obj['cards']['picked_community_chest_cards'] = picked_community_chest_cards_list
    current_gameboard_serial_obj['locations'] = location_serial_obj
    current_gameboard_serial_obj['location_sequence'] = location_sequence_list
    current_gameboard_serial_obj['die_sequence'] = total_die_seq
    current_gameboard_serial_obj['history'] = history_serial_obj
    pruned_gameboard_serial_obj = _prune_serialize_history(current_gameboard_serial_obj)
    with open('result.json', 'w') as fp:
        json.dump(pruned_gameboard_serial_obj, fp)
    fp.close()
    return pruned_gameboard_serial_obj
