import datetime
import fileinput
import os
from utils.trello_query import TrelloConnection

__author__ = 'Pontus'


def update_trello_status():
    conn = TrelloConnection()
    for line in fileinput.input():
        try:
            tstamp, runfolder = line.split()
        except ValueError:
            raise Exception("malformed line input encountered: '{}'".format(line))
        try:
            card = conn.get_card(runfolder)
            if card is None:
                print("a trello card for '{}' could not be found".format(runfolder))
                continue
        except Exception as e:
            print("ERROR: {} - skipping".format(e.message))
            continue
        if card.is_archived():
            continue
        card.mark_archived()
        card.comment(
            "{}: archive was verified on {}".format(
                os.path.basename(__file__),
                datetime.datetime.fromtimestamp(float(tstamp)).isoformat()))
    # Finally, sort the lists on the board
    for listt in conn.lists:
        listt.sort()

if __name__ == '__main__':
    update_trello_status()