# coding:utf-8
from virt_who import *
from virt_who.base import Base
from virt_who.register import Register
from virt_who.testing import Testing

class Testcase(Testing):
    def test_run(self):
        self.vw_case_info(os.path.basename(__file__), case_id='RHEL-133748')
        if self.pkg_check(self.ssh_host(), 'virt-who')[9:15] >= '0.23.3':
            self.vw_case_skip("virt-who version")
        self.vw_case_init()

        # case config
        results = dict()
        cmd1 = self.vw_cli_base() + "--sam -d"
        cmd2 = self.vw_cli_base() + "--satellite6 -d"
        steps = {'step1':cmd1, 'step2':cmd2}

        # case steps
        for step, cmd in sorted(steps.items(),key=lambda item:item[0]):
            logger.info(">>>{0}: run virt-who cli to check sam/satellite options".format(step))
            data, tty_output, rhsm_output = self.vw_start(cmd, exp_send=1)
            s1 = self.op_normal_value(data, exp_error=0, exp_thread=1, exp_send=1)
            results.setdefault(step, []).append(s1)

        # case result
        notes = list()
        notes.append("This case will be deprecated as bug https://bugzilla.redhat.com/show_bug.cgi?id=1368341")
        self.vw_case_result(results, notes)
