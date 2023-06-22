# tfc-rum-basic
Basic RUM Count for TFC / TFE.  This version fixes issue where resources API has not been populated, which impacts any TF workspace not updated since 7/1/2021.

### Caution: 
This version has been tested against a limited sample size.  YMMV

## Usage
```
python3 tfc_rum_count.py [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-a ADDR] [-v] [-p PATH] [-f FILE] [--csv CSV]

Script to output basic Workspace Info (workspace ID, name, version, # resources) as well as an accurate RUM count.

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level (default: ERROR)
  -a ADDR, --addr ADDR  URL for your TFE Server (default: 'https://app.terraform.io')
  -v, --verbose         Verbose will print details for every organization, otherwise only a summary table will appear.
  -p PATH, --path PATH  Path where state files are stored.
  -f FILE, --file FILE  Output file for results   (*** COMING SOON ***)
  --csv CSV             Output in CSV format      (*** COMING SOON ***)
```
### Requires Requests Module
```$ python -m pip install requests```

## Links

### List Workspaces
https://developer.hashicorp.com/terraform/cloud-docs/api-docs/workspaces#list-workspaces
```GET /organizations/:organization_name/workspaces```

### Get Resources
https://developer.hashicorp.com/terraform/cloud-docs/api-docs/workspace-resources#list-workspace-resources
```GET /workspaces/:workspace_id/resources```

### Get Tags
https://developer.hashicorp.com/terraform/cloud-docs/api-docs/workspaces#get-tags
```GET /workspaces/:workspace_id/relationships/tags```



## Optional Environment Variables:
**TF_ADDR**: Address of TFE Server.  If not set, assumes TFC ("https://app.terraform.io"), DO NOT add api/v2 path to the address.


**TF_TOKEN**: valid TFC Token, precendence is:
1. TF_TOKEN
2. ~/.terraform.d/credentials.tfrc.json 
3. User prompt

_TF_ORG_: Organization Name

## Sample Output

### TFC / TFE
```
rryjewski@RKR-MBP14 tfc-rum-basic % python3 tfc_rum_count.py                   
Header
ID                  Name                                    Version   Last Updated Resource Count        RUM   Data RS   Null RS     Total

Org ID: AcmePOV
ws-T81ZYHU6xNQyvLR6 hashicat-azure                          1.4.6     2023-06-08   9                       8         0         1         9
ws-edfasvKsfxyuxqdw azdo-PipelineBootstrap                  1.4.5     2023-04-26   26                     13        13         0        26
ws-RvTKoYSSCdxbrTQ8 Vault-Consul-Demo                       1.4.6     2023-06-08   0                       0         0         0         0
ws-8wZRFjX3grwkwaHX NTierRefArch                            1.4.6     2023-06-08   0                       0         0         0         0
ws-Gxg33zGdHYNn2JSb packer-aws                              1.4.6     2023-06-08   0                       0         0         0         0
ws-Z2BZViGo6HhrS56Y terraform-cloud-backendCLI              1.4.6     2023-06-08   0                       0         0         0         0
ws-1KE8gdLVUqap8WXF HCPPackerTestGCP                        1.4.6     2023-06-08   0                       0         0         0         0
ws-M5dXsDFvkcqJXhA4 CIaC-multicloud                         1.4.6     2023-06-08   0                       0         0         0         0
ws-WqV83vhZkZmZnyJN azure-active-directory-dc-vm            1.4.6     2023-05-30   0                       0         0         0         0
ws-Mgf8GuuoYJ3xUoZq az-caf                                  1.3.4     2022-11-10   0                       0         0         0         0
Org Subtotal:
                                                                                                          21        13         1        35

Org ID: bm_mi_lab
ws-MhvPWvMV8FEaMNKc demo_azure_keyvault                     1.5.0     2023-06-13   8                       7         1         0         8
ws-ygi5Z6ZDyFn67Cj7 demo_aws_bastion                        1.3.2     2023-06-12   6                       1         5         0         6
ws-UZPFPWiULZahSwn7 demo-azure-drift                        1.4.6     2023-06-08   9                       9         0         0         9
ws-5Dt6Q1Yf48hV9kdN demo_vpc_sg_vcs                         1.3.0     2023-04-24   0                       0         0         0         0
ws-AseCdgrHwz1NAXmD demo-azure-complete                     1.4.0     2022-11-14   0                       0         0         0         0
ws-DRdytbz1pLGKZSwA azure_create_keys_native                1.3.9     2023-03-03   6                       4         2         0         6
ws-mu3s2JbztoPHdHZL demo-azure-w-vault                      1.2.1     2022-06-01   0                       0         0         0         0
ws-6Z6GB4suMKNNZZLr prep-all-in-one-hcp                     1.2.0     2022-07-11   0                       0         0         0         0
Org Subtotal:
                                                                                                          21         8         0        29

Org ID: brightblueray
ws-j38PT3bajqjpekVv vault-ent-e2e                           1.4.2     2023-06-21   0                       0         0         0         0
ws-z32hwZxKYJfftFaC rum-test                                1.5.0     2023-06-21   0                       0         0         0         0
ws-4E1VwfEe9zxtuYun demo-pmr-drift-v2                       1.2.9     2022-09-27   5                       5         0         0         5
ws-MKNReg5ycUEKYSM3 04-azure-admin                          latest    2022-09-23   4                       4         0         0         4
ws-yVi45jgbZUm8NhWC demo-vault-cluster                      1.4.0     2023-05-16   0                       0         0         0         0
ws-ynyWW9McBTfSrdgu github-actions-demo                     1.3.1     2023-05-16   0                       0         0         0         0
ws-aEzV1MAm6RySZjcV hcp-vault-ldap-demo                     1.4.2     2023-04-19   3                       2         1         0         3
ws-1MFSpfy6roNuQnHk hcp-platform-demo-config                1.4.2     2023-04-15   43                     41         2         0        43
ws-BU7MpEDsygvYGB8p hcp-packer-tfc-vault-ssh                1.4.2     2023-04-12   3                       2         1         0         3
ws-DzvDxch45C6gbwAy hcp-demo                                1.4.2     2023-04-03   0                       0         0         0         0
ws-hLPTK6RHwtwPCGhd 12-tfe-vault                            1.4.2     2023-04-10   0                       0         0         0         0
ws-8Pnvd3skCR5NjAY6 04-dev-team                             1.4.2     2023-04-10   0                       0         0         0         0
ws-saaDx6TXhN6VwpPc aws-transcribe                          1.4.2     2023-04-10   0                       0         0         0         0
ws-kJFrvJ1oJjxVkXpv hcp-demo-config                         1.4.2     2023-04-04   0                       0         0         0         0
ws-a1f5TbCm5HrMQFbd jwt-vault-cluster                       1.3.1     2023-03-14   0                       0         0         0         0
ws-vKNYoQmS9jcYfswi oidc-github-demo                        1.3.1     2023-03-13   14                     18         1         0        19
ws-2rqExxeeYLDsh3iJ oidc-vault-cluster                      1.3.1     2023-03-03   3                       6         0         0         6
ws-wvApYkKZEy8KfkP5 tfc-agent-debugging                     1.3.8     2023-02-09   0                       0         0         0         0
ws-EAhshNBPXfpnnEGf learn-terraform-cloud-agents            1.3.7     2023-02-03   2                       2         0         0         2
ws-epMQxERwKvY8Hopm idealco-compute-dev                     1.3.5     2022-11-18   7                       6         1         0         7
ws-qochDueRZtBohQ5a idealco-compute-prod                    1.3.5     2022-11-18   7                       6         1         0         7
ws-jgCYrdgqMzs84oHg idealco-landingzone-dev                 1.3.5     2022-11-18   5                       5         0         0         5
ws-PzQKZJUsaCeygAn8 idealco-landingzone-prod                1.3.5     2022-11-18   5                       5         0         0         5
ws-JGQVFxocm2JSyREw terraform-azure-idealco_rg              1.3.1     2022-11-18   5                      10         0         0        10
ws-3FVYREWgKga9R9yB terraform-azure-idealco_compute         1.3.1     2022-11-18   0                       0         0         0         0
ws-ZJrP5vGcf2FUszte demo-pmr-drift-v1                       1.2.7     2022-11-18   0                       0         0         0         0
ws-whoyyWbFKBaHTA3a demo-tf-health                          1.3.1     2022-10-12   25                     22         3         0        25
ws-4E9ETHsEeGEqUZ5c temp_bastion_module_test                1.3.1     2022-10-07   0                       0         0         0         0
ws-tih1X8xj5AiZNUHh 04-azure-vm                             1.2.7     2022-09-29   0                       0         0         0         0
ws-Uv92VYH7SvcXZx2Z demo-vault-infra                        1.2.7     2022-09-10   0                       0         0         0         0
ws-aYs6nDqNcgJhX9t4 vault-ent-cluster                       1.2.7     2022-09-10   0                       0         0         0         0
ws-LZAo9kPz4twtNPnM vault-infra                             latest    2022-08-24   0                       0         0         0         0
ws-nBuidzAcfM7peoqb hcp-packer-demo-prod                    1.2.7     2022-08-24   11                      9         1         1        11
ws-K9JHC2Ew4vc9V6SY hcp-packer-demo-dev                     1.2.7     2022-08-24   8                       7         1         0         8
ws-KyTpMCqCsDjUJ8Yz hcp-packer-demo-admin                   1.2.7     2022-08-24   0                       0         0         0         0
ws-3goCr35s5w3gMmnL vault-cluster                           1.2.7     2022-08-23   0                       0         0         0         0
ws-bs8graiiE4UkGAR2 test-azure-vm                           1.2.2     2022-06-27   8                       7         1         0         8
ws-hrXFyhKpzoBdT5BV rhel-test                               1.2.1     2022-05-25   9                       9         0         0         9
Org Subtotal:
                                                                                                         166        13         1       180

Org ID: glma
Org Subtotal:
                                                                                                           0         0         0         0

Org ID: hc-solutions-engineering
ws-LBKLgM4rCvHt7Yef se-demos                                0.11.5    2020-07-10   467                   467         0         0       467
ws-G6AFRRx3DzckEjqf se-vmware-interim                       0.14.6    2022-03-02   50                     40         5         5        50
ws-upASPqucN3xM22bJ tf-demo-another-ws                      0.12.21   2020-02-19   0                       0         0         0         0
ws-R2GwqnE2remHMqow terraform-ado-demo                      0.12.24   2020-10-29   0                       0         0         0         0
ws-Bt4RRJZPTbPctQSD gy-azure-ops                            0.12.24   2020-04-18   0                       0         0         0         0
ws-58SdqpVPtES6efcL hc-se-demos-2018-reaper                 0.11.13   2020-06-23   42                     37         5         0        42
ws-Bwtvho6VKfdwCtPr se-ado-aks-demo                         0.12.25   2020-05-27   0                       0         0         0         0
ws-mYBjNL1pr1Y1xm7U tf-demo-gy                              0.12.20   2020-03-17   9                       9         0         0         9
ws-nizYoYqzXokMikKE guides-ami-permissions-new              0.11.8    2019-04-03   740                   448       291         1       740
ws-WyoJCfTba7Cz5MWm guides-image-permissions-vault-new      0.11.8    2018-10-10   0                       0         0         0         0
ws-9yjuxbh4Woo1kGp6 guides-image-permissions-vault          0.11.7    2018-09-21   0                       0         0         0         0
Org Subtotal:
                                                                                                        1001       301         6      1308

Org ID: rkr-admin
ws-A4fG8Ge2sxqTN3Sm vault-hcp-prod                          1.3.2     2022-10-10   2                       2         0         0         2
ws-o4gEdL1dwhq49td1 tfc-workspaces-rkr_admin                latest    2022-10-10   3                       2         1         0         3
ws-tpjUiD5n5NppYFJj vault-hcp-prod-config                   1.3.2     2022-10-10   0                       0         0         0         0
Org Subtotal:
                                                                                                           4         1         0         5

Org ID: rryjewski-free
Org Subtotal:
                                                                                                           0         0         0         0

Grand Total:
                                                                                                        1213       336         8      1557
```

### Sample for OSS:
```
ID                  Name                                    Version   Last Updated Resource Count        RUM   Data RS   Null RS     Total

Org ID: /Users/rryjewski/sandbox/github/brightblueray/tfc-rum-basic/samples
n/a                 terraform (1).tfstate                   1.0.9     2023-06-22   0                      25         0         0        25
n/a                 terraform.tfstate                       0.12.17   2023-06-22   0                      42         0         0        42
Org Subtotal:
                                                                                                          67         0         0        67

Grand Total:
                                                                                                          67         0         0        67
```