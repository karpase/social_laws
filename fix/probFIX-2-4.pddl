(define (problem logistics-2-4) (:domain fix)
(:objects
	tech1 tech2 - mechanic
	toolbox st1 st2 st3 st4 - location
	tul1 tul2 tul3 tul4 - tool
        m1 m2 m3 m4 - machine

	(:private tech1
		tech1 - mechanic
	)

	(:private tech2
		tech2 - mechanic
	)

)
(:init
	(mech-at tech1 st4)
	(mech-at tech2 st4)
	(at m1 st1)
	(at m2 st2)
	(at m3 st3)
	(at m4 st4)
	(fit tul1 m1)
	(fit tul1 m2)
	(fit tul2 m3)
	(fit tul2 m4)
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
	)
)
)
