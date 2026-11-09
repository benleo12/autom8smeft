# Three fixes to MadGraph, which runs this file when it loads the model.  Outside MadGraph they do nothing.
#
# 1. MadGraph 3.5 names a combined ALOHA routine (one routine for several Lorentz structures of a vertex)
# in two ways when its name is long enough to be hashed and it ends in a propagator, such as the P0 of a
# massless vector.  The routine is written as ALOHA_<hash of the name with P0>_3 and called as
# ALOHA_<hash of the name>P0_3, so the process does not link (p p > e+ e- g in these models) and
# `check` stops with "name 'ALOHA_...' is not defined".  The wrapper below names the routine the way
# the call does.  Where the two names already agree it changes nothing.
try:
    import aloha.aloha_writers as _aloha_writers
except ImportError:
    _aloha_writers = None
if _aloha_writers is not None and not getattr(_aloha_writers.combine_name, 'dim8auto', False):
    def _combine_name(name, other_names, outgoing, tag=None, unknown_propa=False,
                      _base=_aloha_writers.combine_name):
        propa = [t for t in tag or [] if t.startswith('P')]
        if outgoing and len(propa) == 1 and not unknown_propa:
            rest = [t for t in tag if t != propa[0]]
            return _base(name, other_names, outgoing, rest, True) % {'propa': propa[0]}
        return _base(name, other_names, outgoing, tag, unknown_propa)
    _combine_name.dim8auto = True
    _aloha_writers.combine_name = _combine_name

# 2. MadGraph renames every parameter of a model to mdl_<name> when it loads it, and rewrites the
# expressions a thousand names at a time, each time with one regular expression of a thousand
# alternatives run over every coupling.  These models have more than 4000 parameters and 600 000
# couplings, which makes that renaming take more than an hour of every import (25 seconds with the
# method below), and MadGraph keeps no cached copy of them (some of their gluon vertices carry no
# QCD order).  The method below is MadGraph's own with that loop replaced by one pass, in which every
# whole word of an expression is looked up in the table of new names.  It gives the same expressions,
# since a name is only ever replaced as a whole word.  It replaces the method only where MadGraph's
# text of it is the one it was copied from (MadGraph 3.5.3 to 3.5.6), and leaves any other version
# as it is.
try:
    import madgraph.core.base_objects as _base_objects
except ImportError:
    _base_objects = None
if _base_objects is not None and not getattr(_base_objects.Model.change_parameter_name_with_prefix, 'dim8auto', False):
    import hashlib as _hashlib, inspect as _inspect, re as _re
    try:
        _source = _inspect.getsource(_base_objects.Model.change_parameter_name_with_prefix)
    except (OSError, TypeError):
        _source = ''
    if _hashlib.md5(_source.encode()).hexdigest() == '5f5e144600e4020967e43da8fe93fc28':
        def _change_parameter_name_with_prefix(self, prefix='mdl_'):
            lower_dict = {}
            duplicate = set()
            keys = list(self.get('parameters').keys())
            for key in keys:
                for param in self['parameters'][key]:
                    lower_name = param.name.lower()
                    if not lower_name:
                        continue
                    try:
                        lower_dict[lower_name].append(param)
                    except KeyError:
                        lower_dict[lower_name] = [param]
                    else:
                        duplicate.add(lower_name)
                        _base_objects.logger.debug('%s is defined both as lower case and upper case.' % lower_name)
            if prefix == '' and not duplicate:
                return
            to_change = []
            change = {}
            for key in keys:
                for param in self['parameters'][key]:
                    value = param.name.lower()
                    if value in ['as', 'mu_r', 'zero', 'aewm1', 'g']:
                        continue
                    elif value.startswith(prefix):
                        continue
                    elif value in duplicate:
                        continue
                    elif value:
                        change[param.name] = '%s%s' % (prefix, param.name)
                        to_change.append(param.name)
                        param.name = change[param.name]
            for value in duplicate:
                for i, var in enumerate(lower_dict[value]):
                    to_change.append(var.name)
                    new_name = '%s%s%s' % (prefix, var.name.lower(), ('__%d' % (i + 1) if i > 0 else ''))
                    change[var.name] = new_name
                    var.name = new_name
            assert 'zero' not in to_change
            if not to_change:
                return
            if 'parameter_dict' in self:
                self['parameter_dict'] = dict((change[name] if (name in change) else name, value)
                                              for name, value in self['parameter_dict'].items())
            if hasattr(self, 'map_CTcoup_CTparam'):
                self.map_CTcoup_CTparam = dict((coup_name, [change[name] if (name in change) else name for name in params])
                                               for coup_name, params in self.map_CTcoup_CTparam.items())
            # the one pass, in place of MadGraph's loop over blocks of a thousand names
            word = _re.compile(r'\b(\w+)\b')
            renamed = set(to_change)
            def sub(text):
                return word.sub(lambda m: change.get(m.group(1), m.group(1)), text)
            for key in keys:
                if key == ('external',):
                    continue
                for param in self['parameters'][key]:
                    param.expr = sub(param.expr)
            for key in self['couplings'].keys():
                for coup in self['couplings'][key]:
                    coup.expr = sub(coup.expr)
            ff = [l.formfactors for l in self['lorentz'] if hasattr(l, 'formfactors')]
            for f in set(sum(ff, [])):
                f.value = sub(f.value)
            for part in self['particles']:
                if str(part.get('mass')) in renamed:
                    part.set('mass', sub(str(part.get('mass'))))
                if str(part.get('width')) in renamed:
                    part.set('width', sub(str(part.get('width'))))
                if hasattr(part, 'partial_widths'):
                    for key, value in part.partial_widths.items():
                        part.partial_widths[key] = sub(value)
            if self['running_elements']:
                for el in self['running_elements']:
                    el.value = sub(el.value)
            self['particle_dict'] = ''
            self.get('particle_dict')
        _change_parameter_name_with_prefix.dim8auto = True
        _base_objects.Model.change_parameter_name_with_prefix = _change_parameter_name_with_prefix

# 3. A restriction card (import model dim8_mw-cls1) makes MadGraph drop the couplings that vanish at its
# values, and it looks each name up in a list of those couplings, once for every coupling of every vertex
# and once for every coupling of the model, and takes each emptied vertex out of the list of vertices
# one at a time.  At a class card most of the 600 000 couplings vanish, so the import takes hours.  The
# two methods below are MadGraph's own with the lists looked up as sets and the emptied vertices and the
# dropped couplings taken out in one pass each.  They keep the same vertices, couplings and order, and
# print the same messages.  They replace the methods only where MadGraph's text of them is the one they
# were copied from (MadGraph 3.5.6), and leave any other version as it is.
try:
    import models.import_ufo as _import_ufo
except ImportError:
    _import_ufo = None
if _import_ufo is not None and hasattr(_import_ufo, 'RestrictModel') \
        and not getattr(_import_ufo.RestrictModel.remove_couplings, 'dim8auto', False):
    import hashlib as _hashlib, inspect as _inspect

    def _md5(f):
        try:
            return _hashlib.md5(_inspect.getsource(f).encode()).hexdigest()
        except (OSError, TypeError):
            return ''

    if _md5(_import_ufo.RestrictModel.remove_interactions) == '573690dc9544f386a97b0408e6ef529d' \
            and _md5(_import_ufo.RestrictModel.remove_couplings) == 'd0e1ebcd2d802afa7d95884267dfa84f':
        def _remove_interactions(self, zero_couplings):
            zero = set(zero_couplings)
            mod_vertex = []
            mod_particle_ct = []
            for coup in zero_couplings:
                if coup not in self.coupling_pos:
                    continue
                vertices = [vert for vert in self.coupling_pos[coup] if
                            isinstance(vert, _import_ufo.base_objects.Interaction)]
                for vertex in vertices:
                    modify = False
                    for key, coupling in list(vertex['couplings'].items()):
                        if coupling in zero:
                            modify = True
                            del vertex['couplings'][key]
                        elif coupling.startswith('-'):
                            coupling = coupling[1:]
                            if coupling in zero:
                                modify = True
                                del vertex['couplings'][key]
                    if modify:
                        mod_vertex.append(vertex)
                particles_ct = [pct for pct in self.coupling_pos[coup] if isinstance(pct, tuple)]
                for pct in particles_ct:
                    modify = False
                    for key, coupling in list(pct[0]['counterterm'][pct[1]].items()):
                        if coupling in zero:
                            modify = True
                            del pct[0]['counterterm'][pct[1]][key]
                    if modify:
                        mod_particle_ct.append(pct)
            # the emptied vertices leave the list in one pass, in place of one list.remove each
            emptied = set()
            for vertex in mod_vertex:
                part_name = [part['name'] for part in vertex['particles']]
                orders = ['%s=%s' % (order, value) for order, value in vertex['orders'].items()]
                if not vertex['couplings']:
                    _import_ufo.logger_mod.log(self.log_level, 'remove interactions: %s at order: %s' %
                                               (' '.join(part_name), ', '.join(orders)))
                    emptied.add(id(vertex))
                else:
                    _import_ufo.logger_mod.log(self.log_level, 'modify interactions: %s at order: %s' %
                                               (' '.join(part_name), ', '.join(orders)))
            if emptied:
                self['interactions'][:] = [v for v in self['interactions'] if id(v) not in emptied]
            for pct in mod_particle_ct:
                part_name = pct[0]['name']
                order = pct[1][0]
                loop_parts = ','.join(['(' + ','.join([self.get_particle(p)['name'] for p in part]) + ')'
                                       for part in pct[1][1]])
                if not pct[0]['counterterm'][pct[1]]:
                    _import_ufo.logger_mod.log(self.log_level, 'remove counterterm of particle %s' % part_name +
                                               ' with loop particles (%s)' % loop_parts +
                                               ' perturbing order %s' % order)
                    del pct[0]['counterterm'][pct[1]]
                else:
                    _import_ufo.logger_mod.log(self.log_level, 'Modify counterterm of particle %s' % part_name +
                                               ' with loop particles (%s)' % loop_parts +
                                               ' perturbing order %s' % order)
            for vertex in mod_vertex:
                lorentz_used = set()
                for key in vertex['couplings']:
                    lorentz_used.add(key[1])
                if not lorentz_used:
                    continue
                lorentz_used = list(lorentz_used)
                lorentz_used.sort()
                map = {j: i for i, j in enumerate(lorentz_used)}
                new_lorentz = [l for i, l in enumerate(vertex['lorentz']) if i in lorentz_used]
                new_coup = {}
                for key in vertex['couplings']:
                    new_key = list(key)
                    new_key[1] = map[new_key[1]]
                    new_coup[tuple(new_key)] = vertex['couplings'][key]
                vertex['lorentz'] = new_lorentz
                vertex['couplings'] = new_coup
            return

        def _remove_couplings(self, couplings):
            couplings = set(couplings)
            for name, data in self['couplings'].items():
                data[:] = [coupling for coupling in data if coupling.name not in couplings]

        _remove_interactions.dim8auto = _remove_couplings.dim8auto = True
        _import_ufo.RestrictModel.remove_interactions = _remove_interactions
        _import_ufo.RestrictModel.remove_couplings = _remove_couplings
