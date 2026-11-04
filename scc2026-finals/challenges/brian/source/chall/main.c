#include <stdio.h>
#include <unistd.h>
#include <stdbool.h>

bool debug = false;

struct Befunge {
	int *sp;
	int pcx, pcy;
	int stack[512];
	char grid[25*80];
	char direction;
	bool string_mode;
} interpreter = {
	.sp = interpreter.stack,
	.pcx = 0,
	.pcy = 0,
	.direction = 'R',
	.string_mode = false
};

void move() {
	switch (interpreter.direction) {
		case 'R':
			interpreter.pcx++;
			break;
		case 'L':
			interpreter.pcx--;
			break;
		case 'U':
			interpreter.pcy--;
			break;
		case 'D':
			interpreter.pcy++;
			break;
	}
}

int pop() {
	interpreter.sp--;
	return *interpreter.sp;
}

void push(int value) {
	*interpreter.sp = value;
	interpreter.sp++;
}

void forward() {
	if (debug) {
		printf(
				"PC: (%d, %d, %c), Direction: %c, Stack top: %p (%d, %x)\n",
				interpreter.pcx, interpreter.pcy, interpreter.grid[interpreter.pcy*80 + interpreter.pcx],
				interpreter.direction,
				interpreter.sp,
				*(interpreter.sp - 1),
				*(interpreter.sp - 1)
			);
	}
	int c = interpreter.grid[interpreter.pcy*80 + interpreter.pcx];
	if (interpreter.string_mode && c != '"') {
		*interpreter.sp = c;
		interpreter.sp++;
		return;
	}
	switch (c) {
		case '>':
			interpreter.direction = 'R';
			break;
		case '<':
			interpreter.direction = 'L';
			break;
		case '^':
			interpreter.direction = 'U';
			break;
		case 'v':
			interpreter.direction = 'D';
			break;
		case '+':
			push(pop() + pop());
			break;
		case '-':
			push(-pop() + pop());
			break;
		case '*':
			push(pop() * pop());
			break;
		case '/':
			{
				int b = pop();
				if (b == 0) {
					pop();
					push(0);
				} else {
					int a = pop();
					push(a / b);
				}
			}
			break;
		case '%':
			{
				int b = pop();
				if (b == 0) {
					pop();
					push(0);
				} else {
					int a = pop();
					push(a % b);
				}
			}
			break;
		case '!':
			push(pop() == 0 ? 1 : 0);
			break;
		case '`':
			{
				int b = pop();
				int a = pop();
				push(a > b ? 1 : 0);
			}
			break;
		case ':':
			{
				int a = pop();
				push(a);
				push(a);
			}
			break;
		case '\\':
			{
				int a = pop();
				int b = pop();
				push(a);
				push(b);
			}
			break;
		case '$':
			pop();
			break;
		case '.':
			printf("%d ", pop());
			break;
		case ',':
			printf("%c", pop());
			break;
		case '#':
			move();
			break;
		case 'p':
			{
				int y = pop();
				int x = pop();
				int v = pop();
				if (x >= 0 && x < 80 && y >= 0 && y < 25) {
					interpreter.grid[y*80 + x] = v;
				}
			}
			break;
		case 'g':
			{
				int y = pop();
				int x = pop();
				if (x >= 0 && x < 80 && y >= 0 && y < 25) {
					push(interpreter.grid[y*80 + x]);
				}
			}
			break;
		case '&':
			{
				int input;
				scanf("%d", &input);
				push(input);
			}
			break;
		case '~':
			{
				char input;
				scanf(" %c", &input);
				push(input);
			}
			break;
		case '0' ... '9':
			push(c - '0');
			break;
		case '"':
			interpreter.string_mode = !interpreter.string_mode;
			break;
		case '_':
			interpreter.direction = (pop() == 0) ? 'R' : 'L';
			break;
		case '|':
			interpreter.direction = (pop() == 0) ? 'D' : 'U';
			break;
		default:
			// noop
			break;
	}
}

void run() {
	push(0);
	while (interpreter.grid[interpreter.pcy*80 + interpreter.pcx] != '@') {
		forward();
		move();
		if (interpreter.sp == interpreter.stack || interpreter.sp == interpreter.stack + 512) {
			printf("Stack overflow/underflow detected. Terminating.\n");
			return;
		}
		if (interpreter.pcx < 0 || interpreter.pcx >= 80 || interpreter.pcy < 0 || interpreter.pcy >= 25) {
			printf("Out of bounds detected. Terminating.\n");
			return;
		}
	}
}

void read_program() {
	printf("Enter your Befunge program:\n");
	read(0, interpreter.grid, 80*25);
	getchar();
}

void print_grid() {
	puts(interpreter.grid);
}

void setup() {
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);
}

int main() {
	setup();
	read_program();
	if (debug) {
		print_grid();
	}
	run();
	return 0;
}
