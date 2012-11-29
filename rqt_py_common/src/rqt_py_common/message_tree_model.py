from python_qt_binding.QtGui import QStandardItem, QStandardItemModel

class MessageTreeModel(QStandardItemModel):

    def __init__(self, parent=None):
        # FIXME: why is this not working? should be the same as the following line...
        #super(MessageTreeModel, self).__init__(parent)
        QStandardItemModel.__init__(self, parent)

    def add_message(self, message_instance, message_name='', message_type='', 
                    message_path=''):
        if message_instance is None:
            return
        self._recursive_create_items(self, message_instance, message_name, 
                                     message_type, message_path)

    def _get_toplevel_items(self, index_list):
        items = [self.itemFromIndex(index) for index in index_list]
        uniqueItems = {}
        for item in items:
            while item.parent() is not None:
                item = item.parent()
            if item.row() not in uniqueItems:
                uniqueItems[item.row()] = item
        return uniqueItems.values()

    def _get_data_items_for_path(self, slot_name, slot_type_name, slot_path, 
                                 **kwargs):
        return (QStandardItem(slot_name), QStandardItem(slot_type_name), 
                QStandardItem(slot_path))

    def _recursive_create_items(self, parent, slot, slot_name, slot_type_name, 
                                slot_path, **kwargs):
        row = []
        for item in self._get_data_items_for_path(slot_name, slot_type_name, 
                                                  slot_path, **kwargs):
            item._path = slot_path
            item._user_data = kwargs.get('user_data', None)
            row.append(item)

        is_leaf_node = False
        if hasattr(slot, '__slots__') and hasattr(slot, '_slot_types'):
            for child_slot_name, child_slot_type in zip(slot.__slots__, 
                                                        slot._slot_types):
                child_slot_path = slot_path + '/' + child_slot_name
                child_slot = getattr(slot, child_slot_name)
                self._recursive_create_items(row[0], child_slot, 
                                             child_slot_name, child_slot_type, 
                                             child_slot_path, **kwargs)

        elif type(slot) in (list, tuple) and (len(slot) > 0) and hasattr(slot[0], 
                                                                         '__slots__'):
            child_slot_type = slot_type_name[:slot_type_name.find('[')]
            for index, child_slot in enumerate(slot):
                child_slot_name = '[%d]' % index
                child_slot_path = slot_path + child_slot_name
                self._recursive_create_items(row[0], child_slot, 
                                             child_slot_name, child_slot_type, 
                                             child_slot_path, **kwargs)

        else:
            is_leaf_node = True

        if parent is self and kwargs.get('top_level_row_number', 
                                         None) is not None:
            parent.insertRow(kwargs['top_level_row_number'], row)
        else:
            parent.appendRow(row)

        return (row, is_leaf_node)
