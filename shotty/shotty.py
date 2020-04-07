import boto3
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []

    if project:
        filters = [{'Name':'tag:project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

@click.group()
def cli():
    """Shotty Manage Instances and Snapshots"""

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None, help='Only volumes for project')

def list_snapshots(project):

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(', '.join((
                s.id,
                v.id,
                i.id,
                s.state,
                s.progress,
                s.start_time.strftime('%c')
                )))
    return

@cli.group('volumes')
def volumes():
    """Commands for Volumes"""

@volumes.command('list')
@click.option('--project', default=None, help='Only volumes for project')

def list_volumes(project):

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(', '.join((
            v.id,
            i.id,
            v.state,
            str(v.size) + 'GB',
            v.encrypted and 'Encrypted' or "Not Encrypted"
            )))
    return

@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('snapshot')
@click.option('--project', default=None, help='Take EC2 snapshots')

def create_snapshot(project):
    "Create Snapshot"

    instances = filter_instances(project)

    for i in instances:
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            print("creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description = "Created by Twade to test")
        print("Starting {0}...".format(i.id))
        i.start()
        i.wait_until_running

    print('Snapshot Complete')
        
    return

@instances.command('list')
@click.option('--project', default=None, help='Only instances for project')
def list_instances(project):
    "List EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        tags = {t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('project', '<no project>')
            )))
    return

@instances.command('stop')
@click.option('--project', default=None)

def stop_instances(project):

    instances = filter_instances(project)

    for i in instances:
        print('Stopping {0}...'.format(i.id))
        i.stop()

@instances.command('start')
@click.option('--project', default=None)

def start_instances(project):

    instances = filter_instances(project)

    for i in instances:
        print('Starting {0}...'.format(i.id))
        i.start()

if __name__ == '__main__':
    cli()
