program Main;

uses BaseUnix;

	procedure run;
	var
		choice: integer;

		procedure print_menu;
		begin
			WriteLn('1. Append string');
			WriteLn('2. Print string');
			WriteLn('3. Exit');
			Write('> ');
			flush(Output);
		end;

		procedure repl;
		var
			length: Shortint;
			nr_read: integer;
			s: AnsiString;
			buf: array[0..127] of Char; // 128 elems - even space for nullbyte
		begin
			s := '';
			while True do
			begin
				print_menu();
				ReadLn(choice);
				case choice of
					2: begin
						WriteLn(s);
						flush(Output);
					end;
					3: begin
						Write('Your final string is: ');
						WriteLn(s);
						flush(Output);
						Halt(0);
					end;
				else
					Write('length: ');
					flush(Output);
					ReadLn(length);
					Write('data: ');
					flush(Output);
					nr_read := FpRead(StdInputHandle, buf, Byte(length));
					buf[nr_read] := Char(0);
					s := Concat(s, buf);
				end;
			end;
		end;
	begin
		repl();
	end;

begin
	writeln('Welcome to strcatenator!');
	flush(Output);
	run();
end.
