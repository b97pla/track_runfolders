import os
import trello

__author__ = 'Pontus'


class TrelloConnection(trello.TrelloClient):

    _BOARDNAME = 'Raw data delivery'

    def __init__(self):
        super(TrelloConnection, self).__init__(
            os.getenv('TRELLO_API_KEY'),
            api_secret=os.getenv('TRELLO_API_SECRET'),
            token=os.getenv('TRELLO_API_TOKEN'))
        self.board = self._get_board()
        self.lists = map(RunfolderList, self._get_lists())
        self.cards = map(RunfolderCard, self._get_cards())

    @classmethod
    def _board_is_open(cls, board):
        try:
            return not board.closed
        except AttributeError:
            board.fetch()
            return not board.closed

    def _get_board(self):
        board = filter(lambda x: x.name == self._BOARDNAME and TrelloConnection._board_is_open(x), self.list_boards())
        if len(board) > 1:
            raise Exception("More than one board matching name '{}'".format(self._BOARDNAME))
        return board[0]

    def _get_cards(self):
        return self.board.open_cards()

    def get_card(self, card_name):
        def _name_filter(x):
            return x.name == card_name
        try:
            [card] = filter(_name_filter, self.cards)
            return card
        except ValueError as e:
            if e.message.find('need more than 0') >= 0:
                return None
            raise Exception("More than one card with name '{}' found".format(card_name))

    def archived_runfolders(self):
        def _name(x):
            return x.name
        return map(_name, filter(RunfolderCard.is_archived, self.cards))

    def delivered_runfolders(self):
        def _name(x):
            return x.name
        return map(_name, filter(RunfolderCard.is_delivered, self.cards))

    def _get_lists(self):
        return self.board.open_lists()


class RunfolderList(object):

    def __init__(self, listt):
        self.listt = listt
        self.name = self.listt.name

    def sort(self):
        def _name(x):
            return x.name
        cards = self.listt.list_cards()
        for i, card in enumerate(sorted(cards, key=_name, reverse=True)):
            card.set_pos(i+1)


class RunfolderCard(object):

    _DELIVER_ITEM = 'Deliver data to customer'
    _ARCHIVE_ITEM = 'Archive'

    def __init__(self, card=None):
        self.card = card
        self.name = self.card.name

    def comment(self, text):
        return self.card.comment(text)

    def is_delivered(self):
        return self._delivered('get')

    def is_archived(self):
        return self._archived('get')

    def mark_delivered(self):
        return self._delivered('set', checked=True)

    def mark_archived(self):
        return self._archived('set', checked=True)

    def mark_not_delivered(self):
        return self._delivered('set', checked=False)

    def mark_not_archived(self):
        return self._archived('set', checked=False)

    def is_complete(self):
        # lazy-loading of cards in py-trello is unreliable, so fetch them explicitly
        self.card.fetch()

        def _item_status(x):
            return x['checked']

        def _checklist_complete(x):
            return all(map(_item_status, x.items))
        return all(
            map(_checklist_complete,
                self.card.checklists))

    def __get_checkbox_state(self, filter_fn):
        def _filter_checklist(x):
            return filter(filter_fn, x.items)

        def _checkbox_status(x):
            return x['checked'] # tick status of each checkbox

        def _any_checked(x):
            return any(map(_checkbox_status, _filter_checklist(x))) # any delivered checkbox on the checklist is ticked

        return any(map(_any_checked, self.card.checklists))

    def __set_checkbox_state(self, filter_fn, checked):
        def _filter_checklist(x):
            return filter(filter_fn, x.items)

        def _checklist_has_item(x):
            return len(_filter_checklist(x)) > 0

        def _set_state(x):
            [item] = _filter_checklist(x)
            x.set_checklist_item(item['name'], checked)
            return x

        return map(_set_state, filter(_checklist_has_item, self.card.checklists))

    def _access_checkbox_state(self, op, filter_fn, checked):
        # lazy-loading of cards in py-trello is unreliable, so fetch them explicitly
        self.card.fetch()
        if op == 'get':
            return self.__get_checkbox_state(filter_fn)
        elif op == 'set':
            return self.__set_checkbox_state(filter_fn, checked)

    def _archived(self, op, checked=True):
        def _archive_item(x):
            return x['name'] == self._ARCHIVE_ITEM # filter checboxes based on label
        return self._access_checkbox_state(op, _archive_item, checked)

    def _delivered(self, op, checked=True):
        def _deliver_item(x):
            return x['name'] == self._DELIVER_ITEM # filter checboxes based on label
        return self._access_checkbox_state(op, _deliver_item, checked)

if __name__ == '__main__':
    print("Connecting to trello and sort cards")
    con = TrelloConnection()
    for listt in con.lists[0:2]:
        print("Got '{}'".format(listt.name))
        print("Sorting list")
        listt.sort()
        print("Done")