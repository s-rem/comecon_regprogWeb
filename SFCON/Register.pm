#!/usr/bin/perl
package SFCON::Register;

use SFCON::Register_db;

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
