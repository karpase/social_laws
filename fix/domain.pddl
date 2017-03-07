(define (domain fix)
	(:requirements :typing :multi-agent :unfactored-privacy)
(:types
	agent location tool machine - object
	tool machine - portable
	mechanic - agent
)
(:predicates
	(at ?p - portable ?loc - location)
	(have ?tul - tool ?tech - mechanic)
        (fixed ?mach - machine)
        (fit ?tul - tool ?mach - machine)

	(:private ?agent - agent
		(mech-at ?agent - mechanic ?loc - location)
	)
)

(:action go
	:agent ?tech - mechanic
	:parameters (?loc-from - location ?loc-to - location)
	:precondition 
		(mech-at ?tech ?loc-from)
	:effect (and
		(not (mech-at ?tech ?loc-from))
		(mech-at ?tech ?loc-to)
	)
)

(:action take-tool
	:agent ?tech - mechanic
	:parameters (?tul - tool ?loc - location)
	:precondition (and
		(at ?tul ?loc)
		(mech-at ?tech ?loc)
	)
	:effect (and
		(not (at ?tul ?loc))
		(have ?tul ?tech)
	)
)

(:action put-tool
	:agent ?tech - mechanic
	:parameters (?tul - tool ?loc - location)
	:precondition (and
		(have ?tul ?tech)
		(mech-at ?tech ?loc)
	)
	:effect (and
		(not (have ?tul ?tech))
		(at ?tul ?loc)
	)
)

(:action fix
	:agent ?tech - mechanic
	:parameters (?tul - tool ?loc - location ?mach - machine)
	:precondition (and
		(have ?tul ?tech)
		(mech-at ?tech ?loc)
		(at ?mach ?loc)
                (fit ?tul ?mach)
		(not (fixed ?mach))
	)
	:effect (and (fixed ?mach))
)

)