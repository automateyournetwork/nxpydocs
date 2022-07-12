import sys
import os
import json
import logging
import click
import yaml
from cli import *
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from furl import furl

class NxPyDocs():
    def __init__(self,
                command,
                filetype,
                repo,
                username,
                token,):
        self.command = command
        self.filetype = filetype
        self.repo = repo
        self.username = username
        self.token = token
        self.supported_templates = [
                            # 'show access-lists',
                            # 'show bgp process vrf all',
                            # 'show bgp sessions',
                            # 'show cdp neighbors',
                            # 'show cdp neighbors detail',
                            # 'show environment',
                            'show interface',
                            # 'show interface status',
                            # 'show interface transceiver',
                            'show inventory',
                            # 'show ip arp vrf all',
                            'show ip interface brief',
                            # 'show ip ospf',
                            # 'show ip ospf interface',
                            # 'show ip ospf interface vrf all',
                            # 'show ip ospf neighbors detail',
                            # 'show ip ospf neighbors detail vrf all',
                            # 'show ip route',
                            # 'show ip route vrf all',
                            # 'show mac address-table',
                            # 'show port-channel summary',
                            'show system resources',
                            'show version',
                            #'show vlan'
                            ]

    def nxpydocs(self):
        if self.command == "all":
            self.clone()
            for single_command in self.supported_templates:
                self.command = single_command
                command_output = clid( '%s' % self.command )
                parsed_json = json.loads(command_output)
                self.pick_filetype(parsed_json)
            self.send_to_repo()
            self.cleanup()
        else:
            if self.command in self.supported_templates:
                command_output = clid( '%s' % self.command )
                parsed_json = json.loads(command_output)
                self.clone()
                self.pick_filetype(parsed_json)
                self.send_to_repo()
                self.cleanup()
            else:
                if self.filetype == "json" or "yaml":
                    command_output = clid( '%s' % self.command )
                    parsed_json = json.loads(command_output)                    
                    self.clone()
                    self.pick_filetype(parsed_json)
                    self.send_to_repo()
                    self.cleanup()
                else:
                    click.secho("Show command not templated yet")

    def pick_filetype(self, parsed_json):
        self.get_hostname()        
        if self.filetype == 'json':
            self.json_file(parsed_json)
        elif self.filetype == 'yaml':
            self.yaml_file(parsed_json)
        elif self.filetype == 'html':
            self.html_file(parsed_json)
        elif self.filetype == 'markdown':
            self.markdown_file(parsed_json)
        elif self.filetype == 'csv':
            self.csv_file(parsed_json)
        elif self.filetype == 'mindmap':
            self.mindmap_file(parsed_json)
        elif self.filetype == 'all':
            self.all_files(parsed_json)

    def json_file(self, parsed_json):
        os.chdir("JSON")
        with open('%s %s.json' % (self.hostname,self.command), 'w') as f:
            f.write(json.dumps(parsed_json,indent=4, sort_keys=True))
        os.chdir("..")

    def yaml_file(self, parsed_json):
        os.chdir("YAML")
        dirty_yaml = yaml.dump(json.loads(json.dumps(parsed_json,indent=4, sort_keys=True)), default_flow_style=False)
        clean_yaml = dirty_yaml.replace("!!python/unicode","")
        with open('%s %s.yaml' % (self.hostname,self.command), 'w') as f:
            f.write(clean_yaml)
        os.chdir("..")

    def html_file(self, parsed_json):
        os.chdir("HTML")
        template_dir = Path(__file__).resolve().parent
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        html_template = env.get_template('html.j2')
        html_output = html_template.render(command = self.command,
            data_to_template=parsed_json)
        with open('%s %s.html' % (self.hostname,self.command), 'w') as f:
            f.write(html_output)
        os.chdir("..")

    def markdown_file(self, parsed_json):
        os.chdir("Markdown")
        template_dir = Path(__file__).resolve().parent
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        markdown_template = env.get_template('md.j2')
        markdown_output = markdown_template.render(command = self.command,
            data_to_template=parsed_json)
        with open('%s %s.md' % (self.hostname,self.command), 'w') as f:
            f.write(markdown_output)
        os.chdir("..")

    def csv_file(self, parsed_json):
        os.chdir("CSV")
        template_dir = Path(__file__).resolve().parent
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        csv_template = env.get_template('csv.j2')
        csv_output = csv_template.render(command = self.command,
            data_to_template=parsed_json)
        with open('%s %s.csv' % (self.hostname,self.command), 'w') as f:
            f.write(csv_output)
        os.chdir("..")

    def mindmap_file(self, parsed_json):
        os.chdir("Mindmap")
        template_dir = Path(__file__).resolve().parent
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        mindmap_template = env.get_template('mindmap.j2')
        mindmap_output = mindmap_template.render(command = self.command,
            data_to_template=parsed_json)
        with open('%s %s mindmap.md' % (self.hostname,self.command), 'w') as f:
            f.write(mindmap_output)
        os.chdir("..")

    def all_files(self, parsed_json):
        self.json_file(parsed_json)
        self.yaml_file(parsed_json)
        self.html_file(parsed_json)
        self.markdown_file(parsed_json)
        self.csv_file(parsed_json)
        self.mindmap_file(parsed_json)

    def clone(self):
        os.system("git clone %s nxpydocs" % self.repo)
        os.chdir("nxpydocs")           

    def send_to_repo(self):
        os.system("git add *")
        os.system("git commit -am 'nxpydocs generated this commit'")
        url = furl(self.repo)
        url.username = self.username
        url.password = self.token
        url.tostr()
        os.system("git push %s" % url)

    def cleanup(self):
        os.chdir("..")
        os.system("rm -rf nxpydocs")

    def get_hostname(self):
        show_version_raw = clid("show version" )
        show_version_json = json.loads(show_version_raw)
        self.hostname = show_version_json['host_name']

@click.command()
@click.option('--command',
    prompt='Command',
    help=('''A valid Show Command (i.e. "show ip interface brief")'''),
    required=True)
@click.option('--filetype',
    prompt='Filetype',
    type=click.Choice(['json',
                        'yaml',
                        'html',
                        'csv',
                        'markdown',
                        'mindmap',
                        'all'],
        case_sensitive=True),
    help='Filetype to output captured network state to',
    required=True)
@click.option('--repo',
    prompt='Git Repository',
    help=('The Git repository to send the output files'),
    required=True,envvar="REPO")
@click.option('--username',
    prompt='Git Repository Username',
    help=('The Git repository username'),
    required=True,envvar="USERNAME")
@click.option('--token',
    prompt='Git Repository token',
    help=('The Git repository token'),
    required=True,hide_input=True,envvar="TOKEN",default='none')
def cli(command,
        filetype,
        repo,
        username,
        token
        ):
    invoke_class = NxPyDocs(command,
                            filetype,
                            repo,
                            username,
                            token
                        )
    invoke_class.nxpydocs()

if __name__ == "__main__":
    cli()
