# coding:utf-8
from library import *
from library.config import * 
from library.base import Base
from library.virtwho import Virtwho

class Testcase(Virtwho):
    def test_run(self):
        # Case Header
        case_name = os.path.basename(__file__)
        self.vw_case_info(case_name, "RHEL-134076")
        mode, host_ip, guest_ip = self.vw_env_info()
        server_type, server_ip, owner, env = self.vw_server_info()
        if "libvirt-local" not in mode and "vdsm" not in mode:
            self.vw_case_skip("skipped - this case is not avaialbe for %s" % mode)
        self.vw_env_init(mode)

        # Case Config
        results = dict()
        instance_sku = args_sku['instance_sku_id']
        conf_file = "/etc/virt-who.d/%s.conf" % mode.lower()
        conf_name = "%s_config" % mode.lower()
        self.vw_option_enable("VIRTWHO_DEBUG", filename="/etc/sysconfig/virt-who")
        self.vw_option_update_value("VIRTWHO_DEBUG", '1', filename="/etc/sysconfig/virt-who")
        self.vw_etc_d_mode_create(mode, conf_name, filename=conf_file)

        # Case Steps
        logger.info(">>>step1: set cpu.cpu_socket(s) to 1 in host")
        res = self.system_custom_facts_create(self.ssh_host(), 'cpu.cpu_socket(s)', '1')
        results.setdefault('step1', []).append(res)
 
        logger.info(">>>step2: run virt-who and check the mapping info is sent or not")
        data, tty_output, rhsm_output = self.vw_start()
        res = self.op_normal_value(data, exp_error=0, exp_thread=1, exp_send=1)
        results.setdefault('step2', []).append(res)
 
        logger.info(">>>step3: attach physical sku for host without quantity")
        self.system_sku_unattach(self.ssh_host())
        sku_attrs = self.system_sku_attr(self.ssh_host(), instance_sku, "physical")
        physical_pool_id = sku_attrs['pool_id']
        self.system_sku_attach(self.ssh_host(), pool_id=physical_pool_id)
        output = self.system_sku_consumed(self.ssh_host())
        res1 = self.vw_msg_search(output, instance_sku, exp_exist=True)
        res2 = self.vw_msg_search(output, 'Quantity Used:.*2', exp_exist=True)
        res3 = self.vw_msg_search(output, 'Status Details:.*Subscription is current', exp_exist=True)
        results.setdefault('step3', []).append(res1)
        results.setdefault('step3', []).append(res2)
        results.setdefault('step3', []).append(res3)

        logger.info(">>>step4: attach physical sku for host with quantity=1")
        self.system_sku_unattach(self.ssh_host())
        sku_attrs = self.system_sku_attr(self.ssh_host(), instance_sku, "physical")
        physical_pool_id = sku_attrs['pool_id']
        cmd = "subscription-manager attach --pool=%s --quantity=1" % (physical_pool_id)
        ret, output = self.runcmd(cmd, self.ssh_host(), desc="subscription attach")
        error_msg = 'must be attached using a quantity evenly divisible by 2'
        res = self.vw_msg_search(output, error_msg, exp_exist=True)
        results.setdefault('step3', []).append(res)
        self.system_custom_facts_remove(self.ssh_host())

        logger.info(">>>step5: attach physical sku for host/hypervisor with quantity=2")
        self.system_sku_unattach(self.ssh_host())
        sku_attrs = self.system_sku_attr(self.ssh_host(), instance_sku, "physical")
        physical_pool_id = sku_attrs['pool_id']
        self.system_sku_attach(self.ssh_host(), pool_id=physical_pool_id, quantity=2)
        output = self.system_sku_consumed(self.ssh_host())
        res1 = self.vw_msg_search(output, instance_sku, exp_exist=True)
        res2 = self.vw_msg_search(output, 'Quantity Used:.*2', exp_exist=True)
        res3 = self.vw_msg_search(output, 'Status Details:.*Subscription is current', exp_exist=True)
        results.setdefault('step5', []).append(res1)
        results.setdefault('step5', []).append(res2)
        results.setdefault('step5', []).append(res3)
        self.system_custom_facts_remove(self.ssh_host())

        # Case Result
        self.vw_case_result(results)
if __name__ == "__main__":
    unittest.main()

#===changelog===
# - 2018/06/25 Yuefen<yuefliu@redhat.com>
# - Case created to check virtual pool created or not in guest for Unlimited SKU