**steppyngstounes** / ˈstɛp ɪŋˌstoʊnz /

  1.  *pl. n.* *[Middle English]* "Stone[s] used as [steps] of a stairway;
  also, [stones] in a stream used for crossing."  [*]_
  
      *...while at Calais in 1474 we find 40 'steppyngstounes' bought for
      the stairways of the town.* [*]_

  
  2.  *n.* *[chiefly Pythonic]* A package that provides iterators for
  advancing from `start` to `stop`, subject to algorithms that depend on
  user-defined `value` or `error`.

|CircleCI| |GitHub| |Codacy|

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

.. |CircleCI|      image:: https://circleci.com/gh/guyer/steppyngstounes.svg?style=svg
    :target: https://circleci.com/gh/guyer/steppyngstounes
.. |Codacy|        image:: https://app.codacy.com/project/badge/Grade/442966c7b8a24ca4af23a31fe4ac2df8
    :target: https://www.codacy.com/gh/guyer/steppyngstounes/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=guyer/steppyngstounes&amp;utm_campaign=Badge_Grade
.. |GitHub|        image:: https://img.shields.io/github/contributors/guyer/steppyngstounes.svg
    :target: https://github.com/guyer/steppyngstounes
