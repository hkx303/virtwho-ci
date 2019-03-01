# coding:utf-8
from library import *
from library.base import Base
from library.virtwho import Virtwho

class Testcase(Virtwho):
    def test_run(self):
        # Case Header
        case_name = os.path.basename(__file__)
        self.vw_case_info(case_name, "RHEL-136568")
        mode, host_ip, guest_ip = self.vw_env_info()
        server_type, server_ip, owner, env = self.vw_server_info()
        if self.vw_pkg_check()[9:15] >= '0.23.3':
            self.vw_case_skip("skipped - this case is not avaialbe for virt-who version")
        if "libvirt-local" in mode or "vdsm" in mode:
            self.vw_case_skip("skipped - this case is not avaialbe for %s" % mode)
        self.vw_env_init(mode)

        # Case Config
        results = dict()
        extra_file = "/etc/virt-who.d/extra.conf"
        extra_mode = 'libvirt-remote' if 'xen' in mode else 'xen'
        base_cli = self.vw_cli_base(mode) + "-d"
        if "libvirt-remote" in mode:
            mode = "libvirt"

        # Case Steps
        logger.info(">>>step1: owner option is good value")
        data, tty_output, rhsm_output = self.vw_start(base_cli, exp_send=1)
        res = self.op_normal_value(data, exp_error=0, exp_thread=1, exp_send=1)
        results.setdefault('step1', []).append(res)

        logger.info(">>>step2: owner option is wrong value")
        cli = self.vw_cli_base_update(base_cli, "--%s-owner=.*" % mode, "--%s-owner=xxxxx" % mode)
        data, tty_output, rhsm_output = self.vw_start(cli)
        msg_list = ["owner.* is different|Communication with subscription manager failed"]
        res1 = self.op_normal_value(data, exp_error=1, exp_thread=1, exp_send=0)
        res2 = self.msg_validation(rhsm_output, msg_list, exp_exist=True)
        results.setdefault('step2', []).append(res1)
        results.setdefault('step2', []).append(res2)

        logger.info(">>>step3: owner option is 红帽€467aa value")
        cli = self.vw_cli_base_update(base_cli, "--%s-owner=.*" % mode, "--%s-owner=红帽€467aa" % mode)
        data, tty_output, rhsm_output = self.vw_start(cli)
        msg_list = ["codec can't decode|codec can't encode|Communication with subscription manager failed|owner.* is different"]
        res1 = self.op_normal_value(data, exp_error="1|3", exp_thread=1, exp_send=0)
        res2 = self.msg_validation(rhsm_output, msg_list, exp_exist=True)
        results.setdefault('step3', []).append(res1)
        results.setdefault('step3', []).append(res2)

        logger.info(">>>step4: owner option is null value")
        cli = self.vw_cli_base_update(base_cli, "--%s-owner=.*" % mode, "--%s-owner= " % mode)
        data, tty_output, rhsm_output = self.vw_start(cli)
        msg_list = ["owner not in|owner.* not set|virt-who can't be started"]
        res1 = self.op_normal_value(data, exp_error="0|1|2", exp_thread=0, exp_send=0)
        res2 = self.msg_validation(tty_output, msg_list, exp_exist=True)
        results.setdefault('step4', []).append(res1)
        results.setdefault('step4', []).append(res2)

        logger.info(">>>step5: owner option is disable")
        cli = self.vw_cli_base_update(base_cli, "--%s-owner=.*" % mode, " ")
        data, tty_output, rhsm_output = self.vw_start(cli)
        msg_list = ["owner not in|owner.* not set|virt-who can't be started"]
        res1 = self.op_normal_value(data, exp_error="0|1|2", exp_thread=0, exp_send=0)
        res2 = self.msg_validation(tty_output, msg_list, exp_exist=True)
        results.setdefault('step5', []).append(res1)
        results.setdefault('step5', []).append(res2)

        # Case Result
        self.vw_case_result(results)
if __name__ == "__main__":
    unittest.main()

#===changelog===
# - 2018/12/05 Yuefen<yuefliu@redhat.com>
# - Update to use vw_etc_d_mode_create due to Bug1655626 fix
# - 2018/10/22 Yuefliu<yuefliu@redhat.com>
# - Updated msg_list when owner is 红帽€467aa value
# - 2018/07/16 Eko<hsun@redhat.com>
#- Case created to validate owner option