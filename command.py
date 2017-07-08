import click
import os

plugin_folder = os.path.join(os.path.dirname(__file__), 'scripts')


class MyScripts(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(plugin_folder):
            if filename.endswith('.py'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = os.path.join(plugin_folder, name + '.py')
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)
        if 'cli' in ns:
            return ns['cli']
        if 'main' in ns:
            return ns['main']
        else:
            None


cli = MyScripts(help='Options avalaible for this project')

if __name__ == '__main__':
    cli()
