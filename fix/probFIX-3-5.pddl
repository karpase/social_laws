(define (problem logistics-3-5) (:domain fix)
(:objects
	tech1 tech2 tech3 - mechanic
	toolbox st1 st2 st3 st4 st5 - location
	tul1 tul2 tul3 - tool
        m1 m2 m3 m4 m5 - machine

	(:private tech1
		tech1 - mechanic
	)

	(:private tech2
		tech2 - mechanic
	)

	(:private tech3
		tech3 - mechanic
	)
)
(:init
	(mech-at tech1 st4)
	(mech-at tech2 st2)
	(mech-at tech3 st5)
	(at m1 st1)
	(at m2 st2)
	(at m3 st3)
	(at m4 st5)
	(at m5 st5)
	(fit tul1 m1)
	(fit tul1 m2)
	(fit tul1 m5)
	(fit tul2 m3)
	(fit tul2 m4)
	(fit tul3 m5)   
	(at tul1 toolbox)
	(at tul2 toolbox)
	(at tul3 toolbox)
)
(:goal
	(and
		(fixed m1)
		(fixed m2)
		(fixed m3)
		(fixed m4)
		(fixed m5)
	)
)
)
