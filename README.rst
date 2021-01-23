**steppyngstounes** / ˈstɛp ɪŋˌstoʊnz /

  1.  *pl. n.* *[Middle English]* "Stone[s] used as [steps] of a stairway;
  also, [stones] in a stream used for crossing."  [*]_
  
      *...while at Calais in 1474 we find 40 'steppyngstounes' bought for
      the stairways of the town.* [*]_

  
  2.  *n.* *[chiefly Pythonic]* A package that provides iterators for
  advancing from `start` to `stop`, subject to algorithms that depend on
  user-defined `value` or `error`.

Installation
============

Lorem ipsum dolor sit amet, consectetur adipiscing elit.  Aenean eu blandit
magna, ac pretium odio.  In a nisl erat.  Cras dolor massa, tristique in
lectus vel, elementum tristique lectus.  Phasellus at ipsum eget est
pharetra consectetur.  Nullam euismod hendrerit libero sed commodo.  Duis
et mollis eros.  Nulla mattis scelerisque elit vel blandit.  Vestibulum sit
amet turpis quis augue cursus dapibus.  Duis ut congue est.  Sed sagittis
porta lorem, ac tincidunt lacus pharetra ac.  Pellentesque fringilla felis
id libero dapibus, eu vehicula diam tempus.

Curabitur arcu arcu, rhoncus vitae dapibus vitae, hendrerit ut sem.
Pellentesque odio massa, rhoncus non ligula sit amet, efficitur fringilla
tellus.  Nullam scelerisque quam non ante elementum aliquet.  Nullam
bibendum augue diam, et congue purus ornare at.  Praesent dapibus magna
vitae consectetur congue.  Quisque sed dictum nibh.  Sed imperdiet
condimentum enim, quis tristique nunc consectetur et.

Usage
=====

.. code-block:: python

   old = initial_condition
   for step in SomeStepper(start=0., stop=totaltime, size=dt):
       new = value_fn(step.begin, step.end, step.size)

       if step.succeeded(error=error_fn(new, old)):
           old = new
           # do happy things
       else:
           # do sad things

Interdum et malesuada fames ac ante ipsum primis in faucibus.  Pellentesque
lobortis risus quis dolor interdum, vel auctor urna scelerisque.  Nulla
hendrerit lectus libero, et luctus tellus lobortis ac.  Ut ultrices eros eu
blandit iaculis.  Cras egestas, nibh vel finibus rhoncus, nibh magna tempus
eros, ut aliquet ante dui vel nisl.  Nullam pulvinar risus at dapibus
tempor.  Nulla et tincidunt nisl.  Sed quis felis orci.  Nulla ac tempor
nibh, eget viverra metus.  Ut gravida sit amet nunc in ultrices.  Etiam
scelerisque urna eu imperdiet tempus.  Praesent ultrices urna a felis
vestibulum, vel finibus ipsum accumsan.  Aliquam erat volutpat.

Morbi pellentesque dui sit amet placerat consequat.  Fusce dapibus sem eget
massa bibendum, sit amet cursus ligula dignissim.  Integer convallis lacus
nunc, id dapibus lectus vehicula non.  Aenean tempus quam quis quam
bibendum venenatis.  Nullam pellentesque, tortor vel vulputate vestibulum,
nisi leo blandit ante, molestie dictum urna tortor ut augue.  Vestibulum
ultrices convallis porttitor.  Etiam massa dui, convallis posuere pharetra
vitae, commodo quis dui.

Curabitur sit amet turpis et tortor hendrerit sagittis.  Etiam tristique
quam at elementum consequat.  In egestas lobortis blandit.  Curabitur vel
dolor augue.  Nunc elementum purus sit amet ex eleifend pretium.  Fusce
congue tortor nec enim condimentum varius.  Duis fermentum turpis sed risus
malesuada, eu tincidunt ligula vehicula.  Proin varius diam vitae blandit
rutrum.  Nullam a augue sit amet tortor sollicitudin vulputate.  Quisque
gravida condimentum ultrices.  Proin posuere maximus diam vitae sagittis.
Orci varius natoque penatibus et magnis dis parturient montes, nascetur
ridiculus mus.  Vivamus orci massa, sollicitudin sit amet elit nec,
scelerisque congue enim.  Proin libero velit, imperdiet in vestibulum
vulputate, mattis sit amet justo.

Building Documentation
======================

::

  python setup.py build_sphinx

If the figures do not update

::

  touch doc/modules/*.rst

and repeat.

If the documentation seems not to build correctly in other respects::

  python setup.py build_sphinx --all-files --fresh-env

Documentation can be found in :file:`build/sphinx/html`.

----

.. [*] *Middle English Dictionary*,
    Ed.  Robert E. Lewis, *et al.*,
    Ann Arbor: University of Michigan Press, 1952-2001.
    Online edition in *Middle English Compendium*,
    Ed.  Frances McSparran, *et al.*,
    Ann Arbor: University of Michigan Library, 2000-2018.
    <https://quod.lib.umich.edu/m/middle-english-dictionary/dictionary/MED42815>.
    Accessed 16 December 2020.

.. [*] *Building in England, Down to 1540: A Documentary History*,
    L. F. Salzman, Clarenden Press, Oxford, 1952.
    <https://books.google.com/books?id=WtZPAAAAMAAJ&focus=searchwithinvolume&q=steppyngstounes>.
    Accessed 16 December 2020.
