import logging
from NiaPy import algorithms, benchmarks

__all__ = ['algorithms', 'benchmarks']
__project__ = 'NiaPy'
__version__ = '0.0.0'

VERSION = "{0} v{1}".format(__project__, __version__)

logging.basicConfig()
logger = logging.getLogger('NiaPy')
logger.setLevel('INFO')


class Runner(object):
    # pylint: disable=too-many-instance-attributes, too-many-locals
    def __init__(self, D, NP, nFES, nRuns, useAlgorithms, useBenchmarks,
                 A=0.5, r=0.5, Qmin=0.0, Qmax=2.0, F=0.5, CR=0.9, alpha=0.5,
                 betamin=0.2, gamma=1.0, p=0.5, Lower=-100, Upper=100):
        self.D = D
        self.NP = NP
        self.nFES = nFES
        self.nRuns = nRuns
        self.useAlgorithms = useAlgorithms
        self.useBenchmarks = useBenchmarks
        self.A = A
        self.r = r
        self.Qmin = Qmin
        self.Qmax = Qmax
        self.F = F
        self.CR = CR
        self.alpha = alpha
        self.betamin = betamin
        self.gamma = gamma
        self.p = p
        self.Lower = Lower
        self.Upper = Upper
        self.results = {}

    def __algorithmFactory(self, name, benchmark):
        if name == 'BatAlgorithm':
            bench = benchmarks.utility.Utility.get_benchmark(
                benchmark, self.Lower, self.Upper)
            return algorithms.basic.BatAlgorithm(
                self.D, self.NP, self.nFES, self.A, self.r, self.Qmin, self.Qmax, bench)
        elif name == 'DifferentialEvolutionAlgorithm':
            bench = benchmarks.utility.Utility.get_benchmark(
                benchmark, self.Upper, self.Lower)
            return algorithms.basic.DifferentialEvolutionAlgorithm(
                self.D, self.NP, self.nFES, self.F, self.CR, bench)
        else:
            raise TypeError('Passed benchmark is not defined!')

    def __exportToLog(self):
        logger.info(self.results)

    def run(self, export='log'):
        for alg in self.useAlgorithms:
            self.results[alg] = {}
            for bench in self.useBenchmarks:
                benchName = ''
                if not isinstance(bench, ''.__class__):  # check if passed benchmark is class
                    benchName = str(type(bench).__name__)  # set class name as benchmark name
                else:
                    benchName = bench

                self.results[alg][benchName] = []

                for _i in range(self.nRuns):
                    algorithm = self.__algorithmFactory(alg, bench)
                    self.results[alg][benchName].append(algorithm.run())

        if export == 'log':
            self.__exportToLog()
        elif export == 'xls':
            # TODO: implement export to xls
            pass
        elif export == 'latex':
            # TODO: implement export to latex
            pass
        else:
            raise TypeError('Passed export type is not supported!')
