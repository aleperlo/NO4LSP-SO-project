syms a b c d e h i;
fk = (3-2*c)*c + 1 - b - d;
fkp1 = (3-2*d)*d + 1 - c - e;
fkm1 = (3-2*b)*b + 1 - a - c;
F = expand(1/2*(fk^2 + fkp1^2 + fkm1^2));
Fdiff = expand((subs(F, c, c+h) - subs(F, c, c-h)) / (2*h));
F1 = 1/2*(fk^2 + fkp1^2);
Fn = 1/2*(fk^2 + fkm1^2);
F1diff = expand((subs(F1, c, c+h) - subs(F1, c, c-h)) / (2*h));
Fndiff = expand((subs(Fn, c, c+h) - subs(Fn, c, c-h)) / (2*h));

Hdiff = expand((subs(F, c, c+2*h) - 2*subs(F,c,c+h) + F)/(h^2));
Hdiff1 = expand((subs(F1, c, c+2*h) - 2*subs(F1,c,c+h) + F1)/(h^2));
Hdiffn = expand((subs(Fn, c, c+2*h) - 2*subs(Fn,c,c+h) + Fn)/(h^2));

H1diff = expand((subs(F1, [c, d], [c+h, d+i]) - subs(F1, [c, d], [c+h, d]) - subs(F1, [c, d], [c, d+i]) + F1)/(h*i));

F2 = 1/2*(fk^2);
H2diff = expand(subs(F2, [b, d], [b+h, d+i]) - subs(F2, [b, d], [b+h, d]) - subs(F2, [b, d], [b, d+i]) + F2)/(h*i)