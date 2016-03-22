##What is pulp?

Pulp is a Redhat Community Project and according to [pulp project page](http://www.pulpproject.org/ "The Pulp Project"), 

> Pulp is a platform for managing repositories of content, such as
> software packages, and making it available to a large numbers of
> consumers. If you want to locally mirror all or part of a repository,
> host your own content in a new repository, and manage many types of
> content from multiple sources in one place, Pulp is for you!


Pulp is capable of handling multiple types of repositories, including rpms, ostrees, puppet code and yes docker images. We of-course, are interested in pulps ability to handle docker image repositories. It also has a well documented rest api to allow ease of use.

You can read more about general pulp details in the [pulp project page](http://www.pulpproject.org/ "The Pulp Project").

##Pulp and Docker

Pulp has recently released version 2.8 which added support for docker registry v2 and also cleared up some issues existing in the previous versions.
