import pstats
import cProfile
from datetime import datetime

from route_finding.greedy_dfs import run_greedy_dfs

"""Speed profiling.
Caveat: runs the script in a non-interruptible way, so Ctrl+C won't work!
Use the following command liner instead:
`python -m cProfile -o speed.prof -m kilometer-kampioen.run`

Run the following in any case to inspect the results:
`snakeviz ./speed.prof`
"""

if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with cProfile.Profile() as pr:
        run_greedy_dfs(timestamp)

        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.dump_stats(filename='speed.prof')
