#!/usr/bin/perl
use strict;
use warnings;
package SFCON::Register;

sub new {
    my $class = shift;
    my $self = {};
    return bless $self, $class;
}

sub session_dir {
    my $self = shift;
    return ('/tmp');
}

1;
