(define (problem logistics-5-11) (:domain fix)
(:objects
	tech1 tech2 tech3 tech4 tech5 - mechanic
	toolbox st1 st2 st3 st4 st5 st6 st7 - location
	tul1 tul2 tul3 tul4 - tool
        m1 m2 m3 m4 m5 m6 m7 m8 m9 m10 m11 - machine

	(:private tech1
		tech1 - mechanic
	)

	(:private tech2
		tech2 - mechanic
	)

	(:private tech3
		tech3 - mechanic
	)

	(:private tech4
		tech4 - mechanic
	)

	(:private tech5
		tech5 - mechanic
	)
)
(:init
	(mech-at tech1 st1)
	(mech-at tech2 st4)
	(mech-at tech3 st6)
	(mech-at tech4 toolbox)
	(mech-at tech5 st6)
	(at m1 st1)
	(at m2 st2)
	(at m3 st3)
	(at m4 st4)
	(at m5 st5)
	(at m6 st3)
	(at m7 st5)
	(at m8 st6)
	(at m9 st6)
	(at m10 st7)
	(at m11 st2)
	(fit tul4 m1)
	(fit tul3 m2)
	(fit tul1 m5)
	(fit tul2 m3)
	(fit tul4 m4)
	(fit tul3 m5)   
	(fit tul2 m6)
	(fit tul2 m7)
	(fit tul3 m8)
	(fit tul1 m9)
	(fit tul4 m10)
	(fit tul1 m11)
	(at tul1 toolbox)
	(at tul2 toolbox)
	(at tul3 toolbox)
	(at tul4 toolbox)
)
(:goal
	(and
		(fixed m1)
		(fixed m2)
		(fixed m3)
		(fixed m4)
		(fixed m5)
		(fixed m6)
		(fixed m7)
		(fixed m8)
		(fixed m9)
		(fixed m10)
		(fixed m11)
	)
)
)
