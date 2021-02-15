# aws-script-ec2-stopped
Python Script to extract EC2's stopped in all accounts of the Organization

## Pre-requisitos para ejeuctar el Script
- Tener AWS CLI Instalado y configurado con Access y Secrets Keys
- Tener al menos Python 3.7 instalado
 - Instalar pandas
   - `pip3 install pandas`

## Ejecutar el Script
- Cambiar el Rol `OrganizationAccountAccessRole` en caso de haberlo modificado al crear la Child Accounts https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_access.html.
- `python aws-ec2-script.py`

## Reporte generado
- Se generará un .csv con la siguiente estructura:
  - Account: Account Id de la cuenta de AWS
  - State: Estado de la instancias: stopped
  - InstanceType: Tipo de instancia por ejemplo: _t3.small_
  - VolumeId: Identificador del volumen
  - SnapshotId: Identificador del Snapshot en caso de existir
  - Name: Tage Key Name y Value

## Referencias
 - https://boto3.amazonaws.com/v1/documentation/api/1.9.42/reference/services/ec2.html#EC2.Client.describe_snapshots
 - https://boto3.amazonaws.com/v1/documentation/api/1.9.42/guide/migrationec2.html#checking-what-instances-are-running
 - https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_access.html
