import unittest
from navigation_demo import estimate, observations

class NavigationTests(unittest.TestCase):
    def test_missing_sensors_use_odometry(self):
        rows=[dict(t=i,truth=i+1,odometry=1,gnss=None,radio=None) for i in range(4)]
        self.assertEqual(estimate(rows)['estimates'],[1,2,3,4])

    def test_future_truth_does_not_influence_estimates(self):
        rows=observations(4)
        altered=[dict(r,truth=99999) for r in rows]
        self.assertEqual(estimate(rows,True)['estimates'],estimate(altered,True)['estimates'])
        self.assertEqual(estimate(rows[:90],True)['estimates'],estimate(rows,True)['estimates'][:90])

    def test_both_sensors_absent_and_large_outlier(self):
        row=dict(t=0,truth=0,odometry=0,gnss=1000,radio=None)
        self.assertEqual(estimate([row],True)['estimates'],[0])
        self.assertEqual(estimate([row],True)['rejected_updates'],1)

    def test_seed_replays_identical_observations(self):
        self.assertEqual(observations(7),observations(7))
        self.assertNotEqual(observations(7),observations(8))
