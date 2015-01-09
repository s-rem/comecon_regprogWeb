#!/usr/bin/perl
use strict;
use warnings;
package SFCON::Register_db;

sub new {
    my $class = shift;
    my $self = {};
    return bless $self, $class;
}

# ローカルテスト用ダミー
sub prefix {
    return;
}

sub getprogramnumber {
    my ($self, $sid, $number) = @_;
    my $pgnum = 99;     # とりあえず99番
    return($pgnum);
}
1;
