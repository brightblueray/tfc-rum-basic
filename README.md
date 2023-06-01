# tfc-rum-basic
Basic RUM Count for TFC / TFE

Usage:
```
% python3 tfc_rum_count_basic.py -h        
usage: tfc_rum_count_basic.py [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

Script to output basic Workspace Info (workspace ID, name, version, # resources) as well as an accurate RUM count.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level (default: INFO)
```

## Optional Environment Variables:
_TF_TOKEN_: valid TFC Token, precendence is:
1. TF_TOKEN
2. ~/.terraform.d/credentials.tfrc.json 
3. User prompt

_TF_ORG_: Organization Name

## Sample Output
```
rryjewski@RKR-MBP14 tfc-rum-basic % python3 tfc_rum_count_basic.py
WS ID                   Name                          Version   Resources 
ws-4E1VwfEe9zxtuYun     demo-pmr-drift-v2             1.2.9              5
ws-MKNReg5ycUEKYSM3     04-azure-admin                latest             4
ws-yVi45jgbZUm8NhWC     demo-vault-cluster            1.4.0              0
ws-ynyWW9McBTfSrdgu     github-actions-demo           1.3.1              0
ws-aEzV1MAm6RySZjcV     hcp-vault-ldap-demo           1.4.2              3
ws-1MFSpfy6roNuQnHk     hcp-platform-demo-config      1.4.2             43
ws-j38PT3bajqjpekVv     vault-ent-e2e                 1.4.2              0
ws-BU7MpEDsygvYGB8p     hcp-packer-tfc-vault-ssh      1.4.2              3
ws-DzvDxch45C6gbwAy     hcp-demo                      1.4.2              0
ws-hLPTK6RHwtwPCGhd     12-tfe-vault                  1.4.2              0
ws-8Pnvd3skCR5NjAY6     04-dev-team                   1.4.2              0
ws-saaDx6TXhN6VwpPc     aws-transcribe                1.4.2              0
ws-kJFrvJ1oJjxVkXpv     hcp-demo-config               1.4.2              0
ws-a1f5TbCm5HrMQFbd     jwt-vault-cluster             1.3.1              0
ws-vKNYoQmS9jcYfswi     oidc-github-demo              1.3.1             14
ws-2rqExxeeYLDsh3iJ     oidc-vault-cluster            1.3.1              3
ws-wvApYkKZEy8KfkP5     tfc-agent-debugging           1.3.8              0
ws-EAhshNBPXfpnnEGf     learn-terraform-cloud-agents  1.3.7              2
ws-epMQxERwKvY8Hopm     idealco-compute-dev           1.3.5              7
ws-qochDueRZtBohQ5a     idealco-compute-prod          1.3.5              7
ws-jgCYrdgqMzs84oHg     idealco-landingzone-dev       1.3.5              5
ws-PzQKZJUsaCeygAn8     idealco-landingzone-prod      1.3.5              5
ws-JGQVFxocm2JSyREw     terraform-azure-idealco_rg    1.3.1              5
ws-3FVYREWgKga9R9yB     terraform-azure-idealco_compute1.3.1              0
ws-ZJrP5vGcf2FUszte     demo-pmr-drift-v1             1.2.7              0
ws-whoyyWbFKBaHTA3a     demo-tf-health                1.3.1             25
ws-4E9ETHsEeGEqUZ5c     temp_bastion_module_test      1.3.1              0
ws-tih1X8xj5AiZNUHh     04-azure-vm                   1.2.7              0
ws-Uv92VYH7SvcXZx2Z     demo-vault-infra              1.2.7              0
ws-aYs6nDqNcgJhX9t4     vault-ent-cluster             1.2.7              0
ws-LZAo9kPz4twtNPnM     vault-infra                   latest             0
ws-nBuidzAcfM7peoqb     hcp-packer-demo-prod          1.2.7             11
ws-K9JHC2Ew4vc9V6SY     hcp-packer-demo-dev           1.2.7              8
ws-KyTpMCqCsDjUJ8Yz     hcp-packer-demo-admin         1.2.7              0
ws-3goCr35s5w3gMmnL     vault-cluster                 1.2.7              0
ws-bs8graiiE4UkGAR2     test-azure-vm                 1.2.2              8
ws-hrXFyhKpzoBdT5BV     rhel-test                     1.2.1              9
Total Resources: 167

RUM: 166
Data Resources: 13
Null Resources: 1
Elapsed time: 1.1296995409975352 seconds
```