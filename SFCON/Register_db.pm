#!/usr/bin/perl
package SFCON::Register_db;

sub new {
    my $class = shift;
    my $self = {};
    return bless $self, $class;
}

sub getprogramnumber {
    my ($self, $sid, $number) = @_;
    my $pgnum = 99;     # とりあえず99番
    return($pgnum);
}
1;
