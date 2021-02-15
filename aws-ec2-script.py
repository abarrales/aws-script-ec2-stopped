import botocore
import boto3
import json
import datetime
import pandas as pd 
from dateutil.tz import tzlocal

# Función para Asumir el Rol de la cuenta Child # 
assume_role_cache: dict = {}
def assumed_role_session(role_arn: str, base_session: botocore.session.Session = None):
    base_session = base_session or boto3.session.Session()._session
    fetcher = botocore.credentials.AssumeRoleCredentialFetcher(
        client_creator = base_session.create_client,
        source_credentials = base_session.get_credentials(),
        role_arn = role_arn,
        extra_args = {
        #    'RoleSessionName': None # set this if you want something non-default
        }
    )
    creds = botocore.credentials.DeferredRefreshableCredentials(
        method = 'assume-role',
        refresh_using = fetcher.fetch_credentials,
        time_fetcher = lambda: datetime.datetime.now(tzlocal())
    )
    botocore_session = botocore.session.Session()
    botocore_session._credentials = creds
    return boto3.Session(botocore_session = botocore_session)


def get_ec2_info(account, session, insts):
     # Obtener el cliente de ec2 con la sesión de la cuenta a revisar
    ec2 = session.client('ec2')
        
    # Obtener información de Instancias Detenidas - Status: 'stopped' #
    instances = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])
    
    #insts = []
    # Recorremos las Reservaciones encontradas por cada Cuenta #
    for reservations in instances['Reservations']:
        instances = reservations['Instances']
        #print(instances)
        
        # Recorremos cada una de las instancias encontradas #
        for instance in instances:
            #print(instance)
            #print(instance['State'])
            #print(instance['InstanceType'])
            #print(instance['Tags'])
            
            # Recorremos los TAGS, para busca el Tag: Name y mostrarlo #
            name=''
            tags=instance['Tags']
            for tag in tags:
                if tag['Key'] == 'Name':
                    #print('Key: {} Value: {}'.format(tag['Key'], tag['Value']))
                    name=tag['Value']
            
            
            # Obtenemos el VolumenID #
            VolumeId = instance['BlockDeviceMappings'][0]['Ebs']['VolumeId']
            #print(VolumeId)
            
            # Obtenemos si ese Volumen tiene Snapshot #
            snapshots = ec2.describe_snapshots(Filters=
                    [
                        {'Name': 'status','Values': ['completed',],},
                        {'Name': 'volume-id','Values': [VolumeId,],}
                    ],
                OwnerIds=[account,]
                )
            
            # Si encontramos un SnapshotId lo guardamos para mostrarlo en el reporte #
            SnapshotId=''
            for snapshot in snapshots['Snapshots']:
                #print(snapshot['SnapshotId'])
                SnapshotId=snapshot['SnapshotId']
                break
            
            # Juntamos toda la información para exportarla al reporte #
            insts.append({
                'Account': account,
                'State': instance['State']['Name'],
                'InstanceType': instance['InstanceType'],
                'VolumeId': VolumeId,
                'SnapshotId': SnapshotId,
                'Name': name,
            })
        
    return insts

def get_account_ec2_info(accounts):
    # Array para contener los resultados de las cuentas con instancias detenidas #
    insts=[]
    # Recorremos todas las cuentas listadas en la Organización #
    for account in accounts['Accounts']:
        id_acc = account['Id']
        #print(id_acc)
        
        # Descartamos la Master Account #
        if '590395151234' != id_acc:
            print(id_acc)
            
            # Construimos el ARN con el Rol a asumir 'OrganizationAccountAccessRole' Default por Organizations
            arn="arn:aws:iam::{}:role/{}".format(id_acc, 'OrganizationAccountAccessRole')
            #print(arn)
            
            # Asumimos el Role 'OrganizationAccountAccessRole' y lo guardamos en la variable Session
            session = assumed_role_session(arn)
            
            # Metodo para obtener la información de la Instancias EC2 Detenitas y tu Tag Name. #
            insts = get_ec2_info(id_acc, session, insts)
            #print(insts)
    
    pd.DataFrame(insts).to_csv("file.csv")
    

# Listamos todas las cuentas de la Organización #
client = boto3.client('organizations')
accounts = client.list_accounts()

# Metodo para obtener la información de las instancias que están detenidad #
get_account_ec2_info(accounts)
