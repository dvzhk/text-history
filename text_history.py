class TextHistory:
    _max_pos = 0
    def __init__(self):
        self._text = ""
        self._version = 0
        self._action_log = []

    @property
    def text(self):
        return self._text

    @property
    def version(self):
        return self._version

    def _test_pos(self, pos):
        if pos is None:
            pos = len(self._text)

        if not isinstance(pos, int) or pos > (len(self._text) + 1) or pos < 0:
            raise ValueError("Uncorrect position")

        return pos


    def insert(self, string, pos=None):
        action_to_perform = InsertAction(self._test_pos(pos), string, self._version, self._version+1)

        return self.action(action_to_perform)


    def replace(self, string, pos=None):
        #self.__test_pos__(pos)
        action_to_perform = ReplaceAction(self._test_pos(pos), string, self._version, self._version+1)
        return self.action(action_to_perform)

    def delete(self, pos=0, length=0):
        if length + pos > len(self.text) or length < 0:
            raise ValueError("Incorrect pos, length of text to delete:{},{}. Text length is ".format(pos, length, len(self.text)))
        action_to_perform = DeleteAction(self._test_pos(pos), length, self._version, self._version + 1)
        return self.action(action_to_perform)

    def action(self, action):
        #self._test_pos(action.pos)
        self._text = action.apply(self._text)
        self._version = action.to_version
        self._action_log.append(action)
        return self._version

    def get_actions(self, from_version=0, to_version=None):
        if to_version is not None and to_version > len(self._action_log) or from_version < 0 \
                or to_version is not None and to_version < from_version:
            raise ValueError ("Incorrect version: {}, valid versions 0-{}".format(to_version, len(self._action_log)))
        actions = self._action_log[from_version: to_version]
        print("before", actions)
        if len(actions) > 1:
            return self.optimization(actions)
        else:
            return actions

    def optimization(self, action_log_getted):
        new_action_log = []
        base_action = action_log_getted[0]

        for action in action_log_getted[1:]:
            if isinstance(action, InsertAction) and isinstance(base_action, InsertAction):

                if base_action.pos == action.pos:
                    new_text = action.text + base_action.text
                    base_action = InsertAction(base_action.pos, new_text, base_action.from_version, action.to_version)
                    new_action_log.append(base_action)
                elif action.pos - base_action.pos == len(base_action.text):
                    new_text = base_action.text + action.text
                    base_action =InsertAction(base_action.pos, new_text, base_action.from_version,action.to_version)
                    new_action_log.append(new_action_log.append(base_action))

            elif isinstance(action, DeleteAction) and isinstance(base_action, DeleteAction) \
                    and action.pos == base_action.pos:
                new_length = base_action.length + action.length
                base_action = DeleteAction(base_action.pos, new_length, base_action.from_version, action.to_version)
                new_action_log.append(new_action_log.append(base_action))
            else:
                new_action_log.append(base_action)
                base_action = action
                
        new_action_log.append(base_action)

        return new_action_log



class Action:
    type_action = 0
    def __init__(self, pos, text, from_version, to_version):
        self.text = text
        self.from_version = from_version
        self.to_version = to_version
        self.pos = pos

    def _test_ver(self, from_version, to_version):
        if not isinstance(from_version, int) or\
            not isinstance(to_version, int) or\
            from_version >= to_version or\
            from_version < 0:
            raise ValueError("Incorrect version")

    def apply(self, string):
        self._test_ver(self.from_version, self.to_version)
        return string


class InsertAction(Action):
    type_action = 1
    def apply(self, string):
        self._test_ver(self.from_version, self.to_version)
        return string[0:self.pos] + self.text + string[self.pos:]


class ReplaceAction(Action):
    def apply(self, string):
        self._test_ver(self.from_version, self.to_version)
        return string[0:self.pos] + self.text + string[self.pos + len(self.text):]


class DeleteAction(Action):
    def __init__(self, pos, length, from_version, to_version):
        self.pos = pos
        self.length = length
        self.from_version = from_version
        self.to_version = to_version
    def apply(self, string):
        self._test_ver(self.from_version, self.to_version)
        return string[0:self.pos] + string[self.pos + self.length:]
