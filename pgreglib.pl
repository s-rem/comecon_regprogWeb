#!/usr/bin/perl
use strict;
use Net::SMTP;

# 定数定義
our %CONDEF_CONST = (
    'CONNAME'   => '米魂',
    'CONPERIOD' => '2014-2015',
    'FULLNAME'  => '第54回日本SF大会 米魂',
    'ENTADDR'   => 'program@comecon.com',
    'ENVFROM'   => 'program-return@comecon.com',
    'PGSTAFF'   => 'program-operation@comecon.com',
);

# 共通関数 mail送信
sub doMailSend {
    my (
        $envfrom,   # EnvelopeFrom
        $pAenvto,   # EnvelopeTo配列参照
        $body,      # メール本文
    ) = @_;

    return;

    my $smtp = Net::SMTP->new('127.0.0.1');
    $smtp->mail($envfrom);
    foreach my $envto ( @$pAenvto ) {
        $smtp->to($envto);
    }
    $smtp->data();
    $smtp->datasend( encode('7bit-jis', $body) );
    $smtp->dataend();
    $smtp->quit;
}
1;
#--EOF--
