#!/usr/bin/python2.7

import sys
import os
from sets import Set

DFILE_KEYWORDS = ["requirements", "types", "predicates", "action", "private","functions","constants"]
DFILE_REQ_KEYWORDS = ["typing","strips","multi-agent","unfactored-privacy"]
DFILE_SUBKEYWORDS = ["parameters", "precondition", "effect", "duration"]
PFILE_KEYWORDS = ["objects", "init", "goal","private","metric"]
AFILE_KEYWORDS = ["agents"]

verbose = False


class Predicate(object):
  """A loose interpretation of a predicate used for all similar collections.

  Without a name it is a parameter list.
  It can be typed (or not).
    If typed then args = [[var, type], ...]
    Else args = [var, ...]
  It can be negated.
  It may contain variables or objects in its arguments.
  """
  def __init__(self, name, args, is_typed, is_negated):
    self.name = name
    self.args = args
    self.arity = len(args)
    self.is_typed = is_typed
    self.is_negated = is_negated
    self.ground_facts = set()
    self.agent_param = -1

  def pddl_rep(self):
    """Returns the PDDL version of the instance."""
    rep = ''
    if self.is_negated:
      rep += "(not "
    if self.name != "":
      rep += "(" + self.name + " "
    else:
      rep += "("
    for argument in self.args:
      if self.is_typed:
        rep += argument[0] + " - " + argument[1] + " "
      else:
        rep += argument + " "
    rep = rep[:-1]
    rep += ")"
    if self.is_negated:
      rep += ")"
    return rep

  def __repr__(self):
    return self.pddl_rep()



class Action(object):
  """Represents a simple non-temporal action."""
  def __init__(self, name, parameters, precondition, effect):
    self.name = name
    self.parameters = parameters
    self.precondition = precondition
    self.effect = effect
    self.duration = 1
    self.agent = ""
    self.agent_type = ""

  def pddl_rep(self):
    """Returns the PDDL version of the instance."""
    rep = ''
    rep += "(:action " + self.name + "\n"
    if len(self.parameters.args) == 0:
      rep += "\t:parameters ()" + "\n"
    else:
      rep += "\t:parameters " + str(self.parameters) + "\n"
    if len(self.precondition) == 0:
      rep += "\t:precondition (and )\n"
    elif len(self.precondition) > 1:
      rep += "\t:precondition (and\n"
    else:
      rep += "\t:precondition \n"
    for precon in self.precondition:
      rep += "\t\t" + str(precon) + "\n"
    if len(self.precondition) > 1:
      rep += "\t)\n"
    if len(self.effect) > 1:
      rep += "\t:effect (and\n"
    else:
      rep += "\t:effect \n"
    for eff in self.effect:
      rep += "\t\t" + str(eff) + "\n"
    if len(self.effect) > 1:
      rep += "\t)\n"
    rep += ")\n"
    return rep

  def __repr__(self):
    return self.name #+ str(self.parameters)

class Function(object):
  def __init__(self, obj_list):
    self.obj_list = obj_list

  def pddl_rep(self):
    """Returns the PDDL version of the instance."""
    rep = '('
    for argument in self.obj_list:
      rep += argument + " "
    rep = rep[:-1]
    rep += ") - number"
    return rep

  def __repr__(self):
    return self.pddl_rep()

class GroundFunction(object):
  def __init__(self, obj_list):
    self.obj_list = obj_list

  def pddl_rep(self):
    """Returns the PDDL version of the instance."""
    rep = '(' + self.obj_list[0] + " ("
    for argument in self.obj_list[1:-1]:
      rep += argument + " "
    rep = rep[:-1]
    rep += ") " + self.obj_list[-1] + ") "
    return rep

  def __repr__(self):
    return self.pddl_rep()



class PlanningProblem(object):
  def __init__(self, domainfile, problemfile, parse=True):
    self.domain = '' #String
    self.requirements = set() #[String]
    self.type_list = Set() #{String}
    self.type_list.add('object')
    self.types = {} #Key = supertype_name, Value = type
    self.predicates = [] #[Predicate]
    self.functions = []
    self.ground_functions = []
    self.actions = [] #[Action]
    self.agent_types = set()
    self.agents = set()
    self.problem = '' #String
    self.object_list = Set() #{String}
    self.objects = {} #Key = type, Value = object_name
    self.constants = {} #Key = type, Value = object_name
    self.init = [] #List of Predicates
    self.goal = [] #List of Predicates
    self.metric = False
    
    if parse:
      self.parse_domain(domainfile)
      self.parse_problem(problemfile)
      
      for t in self.agent_types:
        self.agents = self.agents | self.get_objects_of_type(t)
    
      self.requirements = self.requirements - {"multi-agent","unfactored-privacy"}
  
  def get_goal(self, agent):
      i = list(self.agents).index(agent)
      g = []
      
      non_agent_goal = []
      for p in self.goal:
          if p.args[0] in self.agents:
              if p.args[0] == agent:
                  g.append(p)
          else:
              non_agent_goal.append(p)
      
      for j,p in enumerate(non_agent_goal):
          if (j % len(self.agents)) == i:
              g.append(p)
      print agent, g    
      return g
  
  def validate_rational(self):
    pp = PlanningProblem(None,None,False)
    
    pp.domain = self.domain + '-rational'
    pp.requirements = self.requirements
    pp.type_list = self.type_list
    pp.types = self.types
    
    failure = Predicate("failure",[],False,False)
    act = Predicate("act",[],False,False)
    fin = Predicate("fin",[["?a","agent"]],True,False)
    
    pp.predicates = [failure,act,fin] + [Predicate(p.name + "-l", [["?alocal","agent"]] + p.args, p.is_typed, p.is_negated) for p in self.predicates] + [Predicate(p.name + "-g", p.args, p.is_typed, p.is_negated) for p in self.predicates]

    for a in self.agents:
      pp.actions.append(Action("end_s_" + a, Predicate('',[["?alocal","agent"]],True,False), 
                   [Predicate(p.name + "-l",[a] + p.args, p.is_typed, p.is_negated) for p in self.get_goal(a)] +
                   [Predicate(p.name + "-g",p.args, p.is_typed, p.is_negated) for p in self.get_goal(a)], 
                   [Predicate("fin",[a],False,False),Predicate("act",[],False,True)]))      
      for i,f in enumerate(self.get_goal(a)):
        pp.actions.append(Action("end_f_" + a + "_" + str(i), Predicate('',[["?alocal","agent"]],True,False), 
                   [Predicate(p.name + "-l",[a] + p.args, p.is_typed, p.is_negated) for p in self.get_goal(a)] + 
                   [Predicate(f.name + "-g",f.args, f.is_typed, not f.is_negated)], 
                   [Predicate("fin",[a],False,False),Predicate("act",[],False,True),Predicate("failure",[],False,False)]))
              
    for a in self.actions:        
        a_s = Action(a.name + "_s", a.parameters,
                     [Predicate("act",[],False,False)] + 
                     [Predicate(p.name + "-l",[a.parameters.args[0][0]] + p.args, p.is_typed, p.is_negated) for p in a.precondition] +
                     [Predicate(p.name + "-g",p.args, p.is_typed, p.is_negated) for p in a.precondition],
                     [Predicate(p.name + "-l",[a.parameters.args[0][0]] + p.args, p.is_typed, p.is_negated) for p in a.effect] +
                     [Predicate(p.name + "-g",p.args, p.is_typed, p.is_negated) for p in a.effect])
        pp.actions.append(a_s)
        a_f = []
        for i,f in enumerate(a.precondition):
           a_f.append(Action(a.name + "_f_" + str(i), a.parameters, 
                   [Predicate("act",[],False,False)] + 
                   [Predicate(p.name + "-l",[a.parameters.args[0][0]] + p.args, p.is_typed, p.is_negated) for p in a.precondition] + 
                   [Predicate(f.name + "-g",f.args, f.is_typed, not f.is_negated)], 
                   [Predicate(p.name + "-l",[a.parameters.args[0][0]] + p.args, p.is_typed, p.is_negated) for p in a.effect] + 
                   [Predicate("failure",[],False,False)]
                   ))
        pp.actions += a_f

        pp.problem = self.problem + "-rational"
        pp.object_list = []
        pp.objects = {}
        pp.functions = self.functions
        pp.ground_functions = self.ground_functions
        pp.constants = self.objects
        if self.constants:
          pp.constants.update(self.constants)
        pp.init = [act]
        for f in self.init:
            pp.init.append(Predicate(f.name + "-g",f.args, f.is_typed, f.is_negated))
            for a in self.agents:    
              pp.init.append(Predicate(f.name + "-l", [a] + f.args, f.is_typed, f.is_negated))
        pp.goal = [failure] + [Predicate("fin", [a], False, False) for a in self.agents]
    return pp

  def validate_adversarial(self, agent):
    pp = PlanningProblem(None,None,False)    
    
    pp.domain = self.domain + '-adv-' + agent
    pp.requirements = self.requirements
    pp.type_list = self.type_list
    pp.types = self.types
    
    failure = Predicate("failure",[],False,False)
    infocus = Predicate("infocus",[["?a","agent"]],True,False)
    
    pp.predicates = [infocus,failure] + [Predicate(p.name + "-l", p.args, p.is_typed, p.is_negated) for p in self.predicates] +  [Predicate(p.name + "-g", p.args, p.is_typed, p.is_negated) for p in self.predicates]
    
    

    pp.actions = []
    for a in self.actions:
      a_s = Action(a.name + "_s", a.parameters,        
              [Predicate("infocus",[a.parameters.args[0][0]],False,False)] + 
              [Predicate(p.name + "-l",p.args, p.is_typed, p.is_negated) for p in a.precondition] +
              [Predicate(p.name + "-g",p.args, p.is_typed, p.is_negated) for p in a.precondition],
              [Predicate(p.name + "-l",p.args, p.is_typed, p.is_negated) for p in a.effect] +
              [Predicate(p.name + "-g",p.args, p.is_typed, p.is_negated) for p in a.effect])
      pp.actions.append(a_s)
      a_f = []
      for i,f in enumerate(a.precondition):
        a_f.append(Action(a.name + "_f_" + str(i), a.parameters, 
                   [Predicate("infocus",[a.parameters.args[0][0]],False,False)] +  
                   [Predicate(p.name + "-l",p.args, p.is_typed, p.is_negated) for p in a.precondition] + 
                   [Predicate(f.name + "-g",f.args, f.is_typed, not f.is_negated)], 
                   [Predicate(p.name + "-l",p.args, p.is_typed, p.is_negated) for p in a.effect] + 
                   [Predicate("failure",[],False,False)]
                   ))
      pp.actions += a_f
      a_j = Action(a.name + "_j", a.parameters,        
              [Predicate("infocus",[a.parameters.args[0][0]],False,True)] +               
              [Predicate(p.name + "-g",p.args, p.is_typed, p.is_negated) for p in a.precondition],              
              [Predicate(p.name + "-g",p.args, p.is_typed, p.is_negated) for p in a.effect])
      
      pp.actions.append(a_j)
    
      pp.problem = self.problem + '-adv-' + agent
      pp.object_list = []
      pp.objects = {}
      pp.functions = self.functions
      pp.ground_functions = self.ground_functions
      pp.constants = self.objects
      if self.constants:
          pp.constants.update(self.constants)
      pp.init = [Predicate("infocus",[agent],False,False)]
      for f in self.init:
          pp.init.append(Predicate(f.name + "-g",f.args, f.is_typed, f.is_negated))
          pp.init.append(Predicate(f.name + "-l",f.args, f.is_typed, f.is_negated))
      pp.goal = [failure] + [Predicate(p.name + "-l", p.args, p.is_typed, p.is_negated) for p in self.get_goal(agent)]
    return pp

  def validate_alone(self, agent):
    pp = PlanningProblem(None,None,False)    
    
    pp.domain = self.domain + '-alone-' + agent
    pp.requirements = self.requirements
    pp.type_list = self.type_list
    pp.types = self.types
    
    infocus = Predicate("infocus",[["?a","agent"]],True,False)
    
    pp.predicates = [infocus] + [Predicate(p.name, p.args, p.is_typed, p.is_negated) for p in self.predicates]
        

    pp.actions = []
    for a in self.actions:
      a_s = Action(a.name, a.parameters,        
              [Predicate("infocus",[a.parameters.args[0][0]],False,False)] + 
              [Predicate(p.name, p.args, p.is_typed, p.is_negated) for p in a.precondition],
              [Predicate(p.name, p.args, p.is_typed, p.is_negated) for p in a.effect])
      pp.actions.append(a_s)

    pp.problem = self.problem + '-alone-' + agent
    pp.object_list = []
    pp.objects = {}
    pp.functions = self.functions
    pp.ground_functions = self.ground_functions
    pp.constants = self.objects
    if self.constants:
      pp.constants.update(self.constants)
    pp.init = [Predicate("infocus",[agent],False,False)] + self.init
    pp.goal = [Predicate(p.name, p.args, p.is_typed, p.is_negated) for p in self.get_goal(agent)]

    # generate wait actions for each goal fact of each other agent
    for a in self.agents:
      if a != agent:
        a_goal = self.get_goal(a)
        for i,g in enumerate(a_goal):
          notwaited = Predicate("not-waited_" + a + "_" + str(i), [], False, False)
          waited = Predicate("not-waited_" + a + "_" + str(i), [], False, True)
          pp.predicates.append(notwaited)
          pp.init.append(notwaited)
          act_g = Action("wait_" + a + "_" + str(i), 
                        Predicate('', [], True, False), 
                        [notwaited], [g,waited])
          pp.actions.append(act_g)

    return pp

  def validate_rational_waiting(self, waitfor_dict={}):
    pp = PlanningProblem(None,None,False)
    
    pp.domain = self.domain + '-rational'
    pp.requirements = self.requirements
    pp.type_list = self.type_list
    pp.types = self.types
    
    wait_pred_names = set()
    for a in self.actions:
        waitfor = waitfor_dict.get(a.name, set([]))
        for i in waitfor:
            wait_pred_names.add(a.precondition[i].name)
    wait_preds = filter(lambda x: x.name in wait_pred_names, self.predicates)     
    
    
    failure = Predicate("failure",[],False,False)
    act = Predicate("act",[],False,False)
    fin = Predicate("fin",[["?a","agent"]],True,False)
    
    pp.predicates = [failure,act,fin] +\
      [Predicate(p.name + "-l", [["?alocal","agent"]] + p.args, p.is_typed, p.is_negated) for p in self.predicates] +\
      [Predicate(p.name + "-g", p.args, p.is_typed, p.is_negated) for p in self.predicates] +\
      [Predicate(p.name + "-checked", p.args, p.is_typed, p.is_negated) for p in self.predicates] +\
      [Predicate(p.name + "-w", [["?alocal","agent"]] + p.args, p.is_typed, p.is_negated) for p in wait_preds]

    for p in wait_preds:
      pp.actions.append(Action("check_no_" + p.name, Predicate('', p.args, True, False), 
                   [Predicate("fin", [a], False, False) for a in self.agents] + [Predicate(p.name + "-g", map(lambda x: x[0], p.args), False, not p.is_negated)], 
                   [Predicate(p.name + "-checked", map(lambda x: x[0], p.args), False, p.is_negated)]))
      
      pp.actions.append(Action("check_no_waiting_" + p.name, Predicate('', p.args, True, False), 
                   [Predicate("fin", [a], False, False) for a in self.agents] +  [Predicate(p.name + "-w", [a] + map(lambda x: x[0], p.args), False, not p.is_negated) for a in self.agents], 
                   [Predicate(p.name + "-checked", map(lambda x: x[0], p.args), False, p.is_negated)]))

    for a in self.agents:
      pp.actions.append(Action("end_s_" + a, Predicate('',[["?alocal","agent"]],True,False), 
                   [Predicate(p.name + "-l",[a] + p.args, p.is_typed, p.is_negated) for p in self.get_goal(a)] +
                   [Predicate(p.name + "-g",p.args, p.is_typed, p.is_negated) for p in self.get_goal(a)], 
                   [Predicate("fin",[a],False,False),Predicate("act",[],False,True)]))      
      for i,f in enumerate(self.get_goal(a)):
        pp.actions.append(Action("end_f_" + a + "_" + str(i), Predicate('',[["?alocal","agent"]],True,False), 
                   [Predicate(p.name + "-l",[a] + p.args, p.is_typed, p.is_negated) for p in self.get_goal(a)] + 
                   [Predicate(f.name + "-g",f.args, f.is_typed, not f.is_negated)], 
                   [Predicate("fin",[a],False,False),Predicate("act",[],False,True),Predicate("failure",[],False,False)]))
      for i,f in enumerate(wait_preds):
        pp.actions.append(Action("end_w_" + a + "_" + str(i), Predicate('',[["?alocal","agent"]] + f.args,True,False), 
                   [Predicate(p.name + "-l",[a] + p.args, p.is_typed, p.is_negated) for p in self.get_goal(a)] + 
                   [Predicate(f.name + "-w",[a] + map(lambda x: x[0], f.args), False, f.is_negated)], 
                   [Predicate("fin",[a],False,False),Predicate("act",[],False,True),Predicate("failure",[],False,False)]))
              
    for a in self.actions:
        waitfor = waitfor_dict.get(a.name, set([]))
        waitpre = [a.precondition[i] for i in waitfor]
        a_s = Action(a.name + "_s", a.parameters,
                     [Predicate("act",[],False,False)] + 
                     [Predicate(p.name + "-l",[a.parameters.args[0][0]] + p.args, p.is_typed, p.is_negated) for p in a.precondition] +
                     [Predicate(p.name + "-g",p.args, p.is_typed, p.is_negated) for p in a.precondition],
                     [Predicate(p.name + "-l",[a.parameters.args[0][0]] + p.args, p.is_typed, p.is_negated) for p in a.effect] +
                     [Predicate(p.name + "-g",p.args, p.is_typed, p.is_negated) for p in a.effect])
        pp.actions.append(a_s)
        a_f = []
        for i,f in enumerate(a.precondition):
           if i in waitfor:
             a_f.append(Action(a.name + "_w_" + str(i), a.parameters, 
                   [Predicate("act",[],False,False)] + 
                   [Predicate(p.name + "-l",[a.parameters.args[0][0]] + p.args, p.is_typed, p.is_negated) for p in a.precondition] + 
                   [Predicate(f.name + "-g",f.args, f.is_typed, not f.is_negated)], 
                   [Predicate(p.name + "-l",[a.parameters.args[0][0]] + p.args, p.is_typed, p.is_negated) for p in a.effect] +
                   [Predicate(f.name + "-w",[a.parameters.args[0][0]] + f.args, f.is_typed, f.is_negated)] +   
                   [Predicate("failure",[],False,False)]
                   ))
           else:         
             a_f.append(Action(a.name + "_f_" + str(i), a.parameters, 
                   [Predicate("act",[],False,False)] + 
                   [Predicate(p.name + "-l",[a.parameters.args[0][0]] + p.args, p.is_typed, p.is_negated) for p in a.precondition] +
                   [Predicate(p.name + "-g", p.args, p.is_typed, p.is_negated) for p in waitpre] + 
                   [Predicate(f.name + "-g",f.args, f.is_typed, not f.is_negated)], 
                   [Predicate(p.name + "-l",[a.parameters.args[0][0]] + p.args, p.is_typed, p.is_negated) for p in a.effect] + 
                   [Predicate("failure",[],False,False)]
                   ))
        pp.actions += a_f

        pp.problem = self.problem + "-rational"
        pp.object_list = []
        pp.objects = {}
        pp.functions = self.functions
        pp.ground_functions = self.ground_functions
        pp.constants = self.objects
        if self.constants:
          pp.constants.update(self.constants)
        pp.init = [act]
        for f in self.init:
            pp.init.append(Predicate(f.name + "-g",f.args, f.is_typed, f.is_negated))
            for a in self.agents:    
              pp.init.append(Predicate(f.name + "-l", [a] + f.args, f.is_typed, f.is_negated))
        pp.goal = [failure] + [Predicate("fin", [a], False, False) for a in self.agents]
        for p in wait_preds:
            l = []
            self.ground_facts(p, p.ground_facts)
        for p in wait_preds:
            pp.goal += [Predicate(f.name + "-checked", f.args, False, False) for f in p.ground_facts]
            
                
    return pp

  def ground_facts(self, p, l, i=0, subst = []):    
    if i == len(p.args):
        l.add(Predicate(p.name, subst, False, False))     
    else:
        a = p.args[i]                
        t = a[1]                
        objs = self.get_objects_of_type(t)        
        for o in objs:
            self.ground_facts(p, l, i+1, subst + [o])
            
    
  def parse_domain(self, domainfile):
    """Parses a PDDL domain file."""
    
    with open(domainfile) as dfile:
      dfile_array = self._get_file_as_array(dfile)
    #Deal with front/end define, problem, :domain
    if dfile_array[0:4] != ['(', 'define', '(', 'domain']:
      print 'PARSING ERROR: Expected (define (domain ... at start of domain file'
      sys.exit()
    self.domain = dfile_array[4]

    dfile_array = dfile_array[6:-1]
    opencounter = 0
    keyword = ''
    obj_list = []
    is_obj_list = True
    for word in dfile_array:
      if word == '(':
        opencounter += 1
      elif word == ')':
        opencounter -= 1
      elif word.startswith(':'):
        if word[1:] not in DFILE_KEYWORDS:
          pass
        elif keyword != 'requirements':
          keyword = word[1:]
      if opencounter == 0:
        if keyword == 'action':
          self.actions.append(obj_list)
          obj_list = []
        if keyword == 'types':
          for element in obj_list:
            self.types.setdefault('object', []).append(element)
            self.type_list.add('object')
            self.type_list.add(element)
          obj_list = []
        keyword = ''

      if keyword == 'requirements': #Requirements list
        if word != ':requirements':
          if not word.startswith(':'):
            print 'PARSING ERROR: Expected requirement to start with :'
            sys.exit()
          elif word[1:] not in DFILE_REQ_KEYWORDS:
            print 'WARNING: Unknown Rquierement ' + word[1:]
            #print 'Requirements must only be: ' + str(DFILE_REQ_KEYWORDS)
            #sys.exit()
          else:
            self.requirements.add(word[1:])
      elif keyword == 'action':
        obj_list.append(word)
      elif not word.startswith(':'):
        if keyword == 'types': #Typed list of objects
          if is_obj_list:
            if word == '-':
              is_obj_list = False
            else:
              obj_list.append(word)
          else:
            #word is type
            for element in obj_list:
              if not word in self.type_list:
                self.types.setdefault('object', []).append(word)
                self.type_list.add(word)
              self.types.setdefault(word, []).append(element)
              self.type_list.add(element)
              self.type_list.add(word)
            is_obj_list = True
            obj_list = []
        elif keyword == 'constants': #Typed list of objects
          if is_obj_list:
            if word == '-':
              is_obj_list = False
            else:
              obj_list.append(word)
          else:
            #word is type
            for element in obj_list:
              if word in self.type_list:
                self.constants.setdefault(word, []).append(element)
                #self.object_list.add(element)
              else:
                print self.type_list
                print "ERROR unknown type " + word
                sys.exit()
            is_obj_list = True
            obj_list = []
        elif keyword == 'predicates' or keyword == 'private': #Internally typed predicates
          if word == ')':
            if keyword == 'private':
              #print "...skip agent: " +  str(obj_list[:3])
              obj_list = obj_list[3:]
              keyword = 'predicates'
            if len(obj_list) == 0:
              #print "...skip )"
              continue
            p_name = obj_list[0]
            #print "parse predicate: " + p_name + " " + str(obj_list)
            pred_list = self._parse_name_type_pairs(obj_list[1:],self.type_list)
            self.predicates.append(Predicate(p_name, pred_list, True, False))
            obj_list = []
          elif word != '(':
            obj_list.append(word)
        elif keyword == 'functions': #functions
          if word == ')':
            p_name = obj_list[0]
            if obj_list[0] == '-':
              obj_list = obj_list[2:]
            #print "function: " + word + " - " + str(obj_list)
            self.functions.append(Function(obj_list))
            obj_list = []
          elif word != '(':
            obj_list.append(word)

    #Work on the actions
    new_actions = []
    for action in self.actions:
      if action[0] == '-':
        action = action[2:]
      act_name = action[1]
      act = {}
      action = action[2:]
      keyword = ''
      for word in action:
        if word.startswith(':'):
          keyword = word[1:]
        else:
          act.setdefault(keyword, []).append(word)
      self.agent_types.add(act.get('agent')[2])
      agent = self._parse_name_type_pairs(act.get('agent'),self.type_list)
      param_list = agent + self._parse_name_type_pairs(act.get('parameters')[1:-1],self.type_list)
      up_params = Predicate('', param_list, True, False)
      pre_list = self._parse_unground_propositions(act.get('precondition'))
      eff_list = self._parse_unground_propositions(act.get('effect'))
      new_act = Action(act_name, up_params, pre_list, eff_list)

      new_actions.append(new_act)
    self.actions = new_actions

  def parse_problem(self, problemfile):
    """The main method for parsing a PDDL files."""

    with open(problemfile) as pfile:
      pfile_array = self._get_file_as_array(pfile)
    #Deal with front/end define, problem, :domain
    if pfile_array[0:4] != ['(', 'define', '(', 'problem']:
      print 'PARSING ERROR: Expected (define (problem ... at start of problem file'
      sys.exit()
    self.problem = pfile_array[4]
    if pfile_array[5:8] != [')', '(', ':domain']:
      print 'PARSING ERROR: Expected (:domain ...) after (define (problem ...)'
      sys.exit()
    if self.domain != pfile_array[8]:
      print 'ERROR - names don\'t match between domain and problem file.'
      #sys.exit()
    if pfile_array[9] != ')':
      print 'PARSING ERROR: Expected end of domain declaration'
      sys.exit()
    pfile_array = pfile_array[10:-1]

    opencounter = 0
    keyword = ''
    is_obj_list = True
    is_function = False
    obj_list = []
    int_obj_list = []
    int_opencounter = 0
    for word in pfile_array:
      if word == '(':
        opencounter += 1
      elif word == ')':
        if keyword == 'objects':
          obj_list = []
        opencounter -= 1
      elif word.startswith(':'):
        if word[1:] not in PFILE_KEYWORDS:
          print 'PARSING ERROR: Unknown keyword: ' + word[1:]
          print 'Known keywords: ' + str(PFILE_KEYWORDS)
        else:
          keyword = word[1:]
      if opencounter == 0:
        keyword = ''

      if not word.startswith(':'):
        if keyword == 'objects' or keyword == 'private': #Typed list of objects
          #print "word: " + word
          #print "obj_list: " + str(obj_list)
          if keyword == 'private':
              #print "...skip agent: " +  word
              obj_list = []
              keyword = 'objects'
              continue
          if is_obj_list:
            if word == '-':
              is_obj_list = False
            else:
              obj_list.append(word)
          else:
            #word is type
            for element in obj_list:
              if word in self.type_list:
                self.objects.setdefault(word, []).append(element)
                self.object_list.add(element)
              else:
                print self.type_list
                print "ERROR unknown type " + word
                sys.exit()
            is_obj_list = True
            obj_list = []
        elif keyword == 'init':
           if word == ')':
             if obj_list[0] == '=' and is_function == False:
               is_function = True
             else:
               if is_function:
                 #print "function: " + str(obj_list)
                 self.ground_functions.append(GroundFunction(obj_list))
                 is_function = False
               else:
                 #print "predicate: " + str(obj_list)
                 self.init.append(Predicate(obj_list[0], obj_list[1:],False, False))
               obj_list = []
           elif word != '(':
             obj_list.append(word)
        elif keyword == 'goal':
          if word == '(':
            int_opencounter += 1
          elif word == ')':
            int_opencounter -= 1
          obj_list.append(word)
          if int_opencounter == 0:
              self.goal = self._parse_unground_propositions(obj_list)
              obj_list = []
        elif keyword == 'metric':
          self.metric = True
          obj_list = []

  def get_type_of_object(self,obj):
    for t in self.objects.iterkeys():
      if obj in self.objects[t]:
        return t
    for t in self.constants.iterkeys():
      if obj in self.constants[t]:
        return t

  def get_objects_of_type(self,of_type):
    #print "get objects of type " + of_type
    selected_types = {of_type}
    pre_size = 0
    while len(selected_types) > pre_size:
      pre_size = len(selected_types)
      for t in selected_types:
        if t in self.types:
          selected_types = selected_types | set(self.types[t])
    #print selected_types
    selected_objects = set()
    for t in selected_types:
      if t in self.objects:
        selected_objects = selected_objects | set(self.objects[t])
      if t in self.constants:
        selected_objects = selected_objects | set(self.constants[t])
    return selected_objects

  def print_domain(self):
    """Prints out the planning problem in (semi-)readable format."""
    print '\n*****************'
    print 'DOMAIN: ' + self.domain
    print 'REQUIREMENTS: ' + str(self.requirements)
    print 'TYPES: ' + str(self.types)
    print 'PREDICATES: ' + str(self.predicates)
    print 'ACTIONS: ' + str(self.actions)
    print 'FUNCTIONS: ' + str(self.functions)
    print 'CONSTANTS: ' + str(self.constants)
    print '****************'

  def print_problem(self):
    """Prints out the planning problem in (semi-)readable format."""
    print '\n*****************'
    print 'PROBLEM: ' + self.problem
    print 'OBJECTS: ' + str(self.objects)
    print 'INIT: ' + str(self.init)
    print 'GOAL: ' + str(self.goal)
    print 'AGENTS: ' + str(self.agents)
    print '****************'
  
 

         
    
  #Get string of file with comments removed - comments are rest of line after ';'
  def _get_file_as_array(self, file_):
    """Returns the file split into array of words.

    Removes comments and separates parenthesis.
    """
    file_as_string = ""
    for line in file_:
      if ";" in line:
        line = line[:line.find(";")]
      line = (line.replace('\t', '').replace('\n', ' ')
          .replace('(', ' ( ').replace(')', ' ) '))
      file_as_string += line
    file_.close()
    return file_as_string.strip().split()

  def _parse_name_type_pairs(self, array, types):
    """Parses array creating paris of form (name, type).

    Expects array such as [?a, -, agent, ...]."""
    pred_list = []
    if len(array)%3 != 0:
      print "Expected predicate to be typed " + str(array)
      sys.exit()
    for i in range(0, len(array)/3):
      if array[3*i+1] != '-':
        print "Expected predicate to be typed"
        sys.exit()
      if array[3*i+2] in types:
        pred_list.append((array[3*i], array[3*i+2]))
      else:
        print "PARSING ERROR {} not in types list".format(array[3*i+2])
        print "Types list: {}".format(self.type_list)
        sys.exit()
    return pred_list

  def _parse_unground_proposition(self, array):
    """Parses a variable proposition returning dict."""
    negative = False
    if array[1] == 'not':
      negative = True
      array = array[2:-1]
    return Predicate(array[1], array[2:-1], False, negative)

  def _parse_unground_propositions(self, array):
    """Parses possibly conjunctive list of unground propositions.

    Expects array such as [(and, (, at, ?a, ?x, ), ...].
    """
    prop_list = []
    if array[0:3] == ['(', 'and', '(']:
      array = array[2:-1]
    #Split array into blocks
    opencounter = 0
    prop = []
    for word in array:
      if word == '(':
        opencounter += 1
      if word == ')':
        opencounter -= 1
      prop.append(word)
      if opencounter == 0:
        prop_list.append(self._parse_unground_proposition(prop))
        prop = []
    #print array[:array.index(')') + 1]
    return prop_list

  def write_pddl_domain(self, output_file):
    """Writes an unfactored MA-PDDL domain file for this planning problem."""
    file_ = open(output_file, 'w')
    to_write = "(define (domain " + self.domain + ")\n"
    #Requirements
    to_write += "\t(:requirements"
    for r in self.requirements:
      to_write += " :"+r
    to_write += ")\n"
    #Types
    to_write += "(:types\n"
    for type_ in self.types:
      to_write += "\t"
      for key in self.types.get(type_):
        to_write += key + " "
      to_write += "- " + type_
      to_write += "\n"
    to_write += ")\n"
    #Constants
    if len(self.constants) > 0:
      to_write += "(:constants\n"
      for t in self.constants.iterkeys():
        to_write += "\t"
        for c in self.constants[t]:
          to_write += c + " "
        to_write += " - " + t + "\n" 
      to_write += ")\n"
    #Public predicates
    to_write += "(:predicates\n"
    for predicate in self.predicates:
      to_write += "\t{}\n".format(predicate.pddl_rep())
    to_write += ")\n"
    #Functions
    if len(self.functions) > 0:
      to_write += "(:functions\n"
      for function in self.functions:
        to_write += "\t{}\n".format(function.pddl_rep())
      to_write += ")\n"
    #Actions
    for action in self.actions:
      to_write += "\n{}\n".format(action.pddl_rep())
    
    #Endmatter
    to_write += ")" #Close domain defn
    file_.write(to_write)
    file_.close()

  def write_pddl_problem(self, output_file):
    file_ = open(output_file, 'w')
    to_write = "(define (problem " + self.problem +") "
    to_write += "(:domain " + self.domain + ")\n"
    #Objects
    to_write += "(:objects\n"
    for obj in self.object_list:
      to_write += "\t" + obj + " - " + self.get_type_of_object(obj) + "\n"
    to_write += ")\n"
    to_write += "(:init\n"
    for predicate in self.init:
      to_write += "\t{}\n".format(predicate)
    for function in self.ground_functions:
      to_write += "\t{}\n".format(function)
    to_write += ")\n"
    to_write += "(:goal\n\t(and\n"
    for goal in self.goal:
      to_write += "\t\t{}\n".format(goal)
    to_write += "\t)\n)\n"
    if self.metric:
      to_write += "(:metric minimize (total-cost))\n" 
    #Endmatter
    to_write += ")"
    file_.write(to_write)
    file_.close()

  def write_addl(self, output_file):
    file_ = open(output_file, 'w')
    to_write = "(define (problem " + self.problem +") "
    to_write += "(:domain " + self.domain + ")\n"
    #Objects
    to_write += "(:agents"
    for obj in self.agents:
      to_write += " " + obj 
    to_write += ")\n"
    to_write += ")"
    file_.write(to_write)
    file_.close()

  def write_agent_list(self, output_file):
    file_ = open(output_file, 'w')
    to_write = ""
    for obj in self.agents:
      to_write += obj + "\n"
    file_.write(to_write)
    file_.close()

def read_waitfor(filename):
  d = {}
  with open(filename) as f:
    for line in f:
      l = line.rstrip('\n').split(' ')
      action_name = l[0]
      precon_indices = set(map(int,l[1:]))
      d[action_name] = precon_indices
  return d
    


if __name__ == "__main__":
  if len(sys.argv) < 4:
    print 'Requires 4 args'
    print 'arg1: folder'
    print 'arg2: domain'
    print 'arg3: problem'
    print 'arg4: output folder'
  else:
    pp = PlanningProblem(sys.argv[1] + "/" + sys.argv[2] + ".pddl", sys.argv[1] + "/" + sys.argv[3] + ".pddl")
    waitfor_dict = read_waitfor(sys.argv[1] + "/waitfor.txt")
    
    rpp = pp.validate_rational_waiting(waitfor_dict)
    path=os.path.join(os.path.abspath(sys.argv[4]),"rational_wait",os.path.basename(os.path.normpath(sys.argv[1])))
    if not os.path.exists(path):
      os.makedirs(path)
    rpp.write_pddl_domain(os.path.join(path,"domain_" + sys.argv[3] + ".pddl"))
    rpp.write_pddl_problem(os.path.join(path, sys.argv[3] + ".pddl"))
    
    rpp = pp.validate_rational()
    path=os.path.join(os.path.abspath(sys.argv[4]),"rational_smpl",os.path.basename(os.path.normpath(sys.argv[1])))
    if not os.path.exists(path):
      os.makedirs(path)
    rpp.write_pddl_domain(os.path.join(path,"domain_" + sys.argv[3] + ".pddl"))
    rpp.write_pddl_problem(os.path.join(path, sys.argv[3] + ".pddl"))
        
    for a in pp.agents:
      app = pp.validate_adversarial(a)
      path=os.path.join(os.path.abspath(sys.argv[4]),"adversarial",os.path.basename(os.path.normpath(sys.argv[1])),sys.argv[3],a)      
      if not os.path.exists(path):
        os.makedirs(path)
      app.write_pddl_domain(os.path.join(path,"domain.pddl"))
      app.write_pddl_problem(os.path.join(path,"problem.pddl"))
      
    for a in pp.agents:
      app = pp.validate_alone(a)
      path=os.path.join(os.path.abspath(sys.argv[4]),"alone",os.path.basename(os.path.normpath(sys.argv[1])),sys.argv[3],a)      
      if not os.path.exists(path):
        os.makedirs(path)
      app.write_pddl_domain(os.path.join(path,"domain.pddl"))
      app.write_pddl_problem(os.path.join(path,"problem.pddl"))
    


    
    #rpp.write_addl(sys.argv[4] + "/" + sys.argv[3] + ".addl")
    #rpp.write_agent_list(sys.argv[4] + "/" + sys.argv[3] + ".agents")

    



