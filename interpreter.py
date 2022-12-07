from sys import argv

class Node:
    def __init__(self, symbol='_', prev=None, next=None):
        self.symbol = symbol
        self.next = next
        self.prev = prev

class Tape:
    def __init__(self, s: str):
        self.pointer = Node(s[0] if s else '_')
        self.head = self.pointer
        curr = self.pointer
        for i in range(1, len(s)):
            curr.next = Node(s[i], prev=curr)
            curr = curr.next

    def get_current_symbol(self):
        return self.pointer.symbol

    def add_node(self, direction):
        if direction in ('L', 'l'):
            self.pointer.prev = Node(next=self.pointer)
            self.head = self.pointer.prev
        else:
            self.pointer.next = Node(prev=self.pointer)
    
    def move(self, write_symbol, direction):
        assert len(write_symbol) == 1, f"Invalid symbol! {write_symbol}"

        if write_symbol != '*':
            self.pointer.symbol = write_symbol
        
        if direction in ('l', 'L'):
            if not self.pointer.prev:
                self.add_node(direction)
            self.pointer = self.pointer.prev
        elif direction in ('r', 'R'):
            if not self.pointer.next:
                self.add_node(direction)
            self.pointer = self.pointer.next
        elif direction == '*':
            pass
        else:
            raise Exception("Invalid movement direction")
    

class TM:
    def __init__(self, initial=None):
        self.initial = initial
        self.state = None
        self.transitions = {}
        self.tape = None
        self.steps = 0

    def parse_from_file(self, filepath):
        self.transitions = {}
        self.charset = set()
        with open(filepath, 'r') as f:
            for i, l in enumerate(f.readlines()):
                l = l.split(";")[0].strip()
                if not l:
                    continue
                l = l.split()
                if len(l) != 5:
                    raise Exception(f"ParseError line: {i+1}\n{' '.join(x for x in l)}\nfound {len(l)} elements")
                state, read, write, d, next_state = l

                self.transitions.setdefault(state, {})[read] = (write, d, next_state)
                self.charset.add(read)
                self.charset.add(write)
            
                if self.initial == None:
                    self.initial = state
                    self.state = state
            
            self.charset.difference_update({"*", "_"})

    def reset(self, s):
        self.steps = 0
        self.state = self.initial
        self.tape = Tape(s)

    def step(self):
        ch = self.tape.get_current_symbol()
        try:
            state_dict = self.transitions[self.state]
            if ch in state_dict:
                write, d, next_state = state_dict[ch]
            elif '*' in state_dict:
                write, d, next_state = state_dict['*']
            else:
                raise KeyError
        except KeyError:
            self.state = "halt-reject, transition for state not found"
            return False
        self.tape.move(write, d)
        self.state = next_state
        self.steps += 1
        if len(self.state) >= 4 and self.state[:4] == 'halt':
            return False
        return True


if len(argv) < 3:
    print('Usage: python3 interpreter.py <TM_file> <input_file>')
    exit(1)

tm = TM()
tm.parse_from_file(argv[1])
input_str = ''
with open(argv[2], 'r') as f:
    # replace new lines with blank space chars
    input_str = f.read().strip().replace('\n', '_')

tm.reset(input_str)

while tm.step():
    pass

# print remaining symbols on tape
curr = tm.tape.head
output = []
while curr:
    output.append(curr.symbol)
    curr = curr.next

print(''.join(output).replace('_', ' ').strip())