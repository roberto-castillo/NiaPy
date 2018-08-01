# encoding=utf8
# pylint: disable=mixed-indentation, trailing-whitespace, multiple-statements, attribute-defined-outside-init, logging-not-lazy, unused-argument, singleton-comparison, no-else-return, line-too-long, arguments-differ, no-self-use, superfluous-parens
import logging
from math import ceil
from numpy import argmin, argsort
from NiaPy.algorithms.algorithm import Algorithm, Individual

logging.basicConfig()
logger = logging.getLogger('NiaPy.algorithms.basic')
logger.setLevel('INFO')

__all__ = ['EvolutionStrategy1p1', 'EvolutionStrategyMp1', 'EvolutionStrategyMpL', 'EvolutionStrategyML']

class IndividualES(Individual):
	def __init__(self, **kwargs):
		task, x, rho = kwargs.get('task', None), kwargs.get('x', None), kwargs.get('rho', 1)
		if rho != None: self.rho = rho
		elif task != None or x != None: self.rho = 1.0
		Individual.__init__(self, **kwargs)

class EvolutionStrategy1p1(Algorithm):
	r"""Implementation of (1 + 1) evolution strategy algorithm. Uses just one individual.

	**Algorithm:** (1 + 1) Evolution Strategy Algorithm
	**Date:** 2018
	**Authors:** Klemen Berkovič
	**License:** MIT
	**Reference URL:**
	**Reference paper:**
	"""
	def __init__(self, **kwargs):
		if kwargs.get('name', None) == None: Algorithm.__init__(self, name='(1+1)-EvolutionStrategy', sName='(1+1)-ES', **kwargs)
		else: Algorithm.__init__(self, **kwargs)

	def setParameters(self, **kwargs): self.__setParams(**kwargs)

	def __setParams(self, mu=1, k=10, c_a=1.1, c_r=0.5, **ukwargs):
		r"""Set the arguments of an algorithm.

		**Arguments**:
		mu {integer} --
		k {integer} --
		c_a {real} --
		c_r {real} --
		"""
		self.mu, self.k, self.c_a, self.c_r = mu, k, c_a, c_r
		if ukwargs: logger.info('Unused arguments: %s' % (ukwargs))

	def mutate(self, x, rho): return x + self.rand.normal(0, rho, len(x))

	def updateRho(self, rho, k):
		phi = k / self.k
		if phi < 0.2: return self.c_r * rho
		elif phi > 0.2: return self.c_a * rho
		else: return rho

	def runTask(self, task):
		c, ki = IndividualES(task=task, rand=self.rand), 0
		while not task.stopCondI():
			if task.Iters % self.k == 0: c.rho, ki = self.updateRho(c.rho, ki), 0
			cn = [task.repair(self.mutate(c.x, c.rho)) for _i in range(self.mu)]
			cn_f = [task.eval(cn[i]) for i in range(self.mu)]
			ib = argmin(cn_f)
			if cn_f[ib] < c.f: c.x, c.f, ki = cn[ib], cn_f[ib], ki + 1
		return c.x, c.f

class EvolutionStrategyMp1(EvolutionStrategy1p1):
	r"""Implementation of (mu + 1) evolution strategy algorithm. Algorithm creates mu mutants but into new generation goes only one individual.

	**Algorithm:** ($\mu$ + 1) Evolution Strategy Algorithm
	**Date:** 2018
	**Authors:** Klemen Berkovič
	**License:** MIT
	**Reference URL:**
	**Reference paper:**
	"""
	def __init__(self, **kwargs): EvolutionStrategy1p1.__init__(self, name='(mu+1)-EvolutionStrategy', sName='(mu+1)-ES', **kwargs)

	def setParameters(self, **kwargs):
		mu = kwargs.pop('mu', 40)
		EvolutionStrategy1p1.setParameters(self, mu=mu, **kwargs)

class EvolutionStrategyMpL(EvolutionStrategy1p1):
	r"""Implementation of (mu + lambda) evolution strategy algorithm. Mulation creates lambda individual. Lambda individual compete with mu individuals for survival, so only mu individual go to new generation.

		**Algorithm:** ($mu$ + $lambda$) Evolution Strategy Algorithm
	**Date:** 2018
	**Authors:** Klemen Berkovič
	**License:** MIT
	**Reference URL:**
	**Reference paper:**
	"""
	def __init__(self, **kwargs):
		if kwargs.get('name', None) == None: EvolutionStrategy1p1.__init__(self, name='(mu+lambda)-EvolutionStrategy', sName='(mu+lambda)-ES', **kwargs)
		else: EvolutionStrategy1p1.__init__(self, **kwargs)

	def setParameters(self, **kwargs):
		EvolutionStrategy1p1.setParameters(self, **kwargs)
		self.__setParams(**kwargs)

	def __setParams(self, lam=45, **ukwargs):
		r"""Set the arguments of an algorithm.

		**Arguments**:
		lam {integer} -- Number of new individual generated by mutation
		"""
		self.lam = lam
		if ukwargs: logger.info('Unused arguments: %s' % (ukwargs))

	def mutate(self, x, rho): return x + self.rand.normal(0, rho, len(x))

	def updateRho(self, pop, k):
		phi = k / self.k
		if phi < 0.2:
			for i in pop: i.rho = self.c_r * i.rho
		elif phi > 0.2:
			for i in pop: i.rho = self.c_a * i.rho

	def changeCount(self, a, b):
		k = 0
		for e in b:
			if e not in a: k += 1
		return k

	def mutateRepair(self, pop, task):
		i = self.rand.randint(self.mu)
		return task.repair(self.mutate(pop[i].x, pop[i].rho))

	def runTask(self, task):
		c, ki = [IndividualES(task=task, rand=self.rand) for _i in range(self.mu)], 0
		while not task.stopCondI():
			if task.Iters % self.k == 0: _, ki = self.updateRho(c, ki), 0
			cm = [self.mutateRepair(c, task) for i in range(self.lam)]
			cn = [IndividualES(x=cm[i], task=task) for i in range(self.lam)]
			cn.extend(c)
			cn = [cn[i] for i in argsort([i.f for i in cn])[:self.mu]]
			ki += self.changeCount(c, cn)
			c = cn
		return c[0].x, c[0].f

class EvolutionStrategyML(EvolutionStrategyMpL):
	r"""Implementation of (mu, lambda) evolution strategy algorithm. Algorithm is good for dynamic environments. Mu individual create lambda chields. Only best mu chields go to new generation. Mu parents are discarded.

	**Algorithm:** ($mu$ + $lambda$) Evolution Strategy Algorithm
	**Date:** 2018
	**Authors:** Klemen Berkovič
	**License:** MIT
	**Reference URL:**
	**Reference paper:**
	"""
	def __init__(self, **kwargs):
		if kwargs.get('name', None) == None: EvolutionStrategyMpL.__init__(self, name='(mu,lambda)-EvolutionStrategy', sName='(mu,lambda)-ES', **kwargs)
		else: EvolutionStrategyMpL.__init__(self, **kwargs)

	def newPop(self, pop):
		pop_s = argsort([i.f for i in pop])
		if self.mu < self.lam: return [pop[i] for i in pop_s[:self.mu]]
		q, npop = ceil(self.mu / self.lam), list()
		for j in range(q):
			diff = self.mu - (self.lam * j)
			npop.extend([pop[i] for i in (pop_s if diff >= self.lam else pop_s[:diff])])
		return npop

	def runTask(self, task):
		c = [IndividualES(task=task, rand=self.rand) for _i in range(self.mu)]
		while not task.stopCondI():
			cm = [self.mutateRepair(c, task) for i in range(self.lam)]
			cn = [IndividualES(x=cm[i], task=task) for i in range(self.lam)]
			c = self.newPop(cn)
		return c[0].x, c[0].f

# vim: tabstop=3 noexpandtab shiftwidth=3 softtabstop=3
