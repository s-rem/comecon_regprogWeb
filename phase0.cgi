#!/usr/bin/perl
# 企画申込フェーズ０
#
use lib ((getpwuid($<))[7]) . '/local/lib/perl5';
use strict;
use CGI;
use CGI::Session;
use Net::SMTP;
use CGI::Carp qw(fatalsToBrowser); 
use HTML::Template;
use File::Basename;
use SFCON::Register;
use SFCON::Register_db;


use Encode::Guess qw/ shiftjis euc-jp 7bit-jis /;
use Encode qw/ decode encode from_to/;

my $register = SFCON::Register->new;
my $cgi = CGI->new;
my $dbaccess = SFCON::Register_db->new;

my $mail = $cgi->param("mail");
my $name = $cgi->param("name"); 
my $reg_num = $cgi->param("reg_num"); 
my $reg_code = $cgi->param("reg_code");

my $html_out = HTML::Template->new(filename => 'phase0-tmpl.html');
my $mail_out = HTML::Template->new(filename => 'mail-tmpl.txt');

my $session=CGI::Session->new(undef,undef,{Directory=>$register->session_dir()});
#セッションidの生成．ディレクトリ.sessionは予め作っておく
$session->expire('+720m'); #有効期限の設定．１２時間
$session->param('reg_code',$reg_code); #セッション経由で引き渡す項目と値
$session->param('reg_num',$reg_num); #セッション経由で引き渡す項目と値
$session->param('email',$mail); #セッション経由で引き渡す項目と値
$session->param('p1_name',$name); #セッション経由で引き渡す項目と値
$session->param('p1_nafda',$name); #セッション経由で引き渡す項目と値
$session->param('phase','1-1'); #セッション経由で引き渡す項目と値

my $reg_class = $dbaccess->get_reg_class($reg_code);

my $inh_stat = 1;

my ($filename, $pathname) = fileparse($cgi->self_url);
### >> for test comment
#$pathname =~ s/^http:/https:/g ;
### << for test comment
my $next_uri = $pathname . 'phase1.cgi?ID='.$session->id;

my $out;

if($reg_class eq 'F'){
	print $cgi->redirect($next_uri);
	exit(0);
}

if($inh_stat){
	#mail本文の生成。
	
	$mail_out->param(NAME => $name);
	$mail_out->param(URI => $next_uri);
	
	my $smtp = Net::SMTP->new('127.0.0.1');
	
	$smtp->mail('program-return@koicon.com');
	smtp->to($mail);
	
	$smtp->data();
	$smtp->datasend(encode('MIME-Header-ISO_2022_JP',decode('utf8',
		"From: 第52回日本SF大会" . ' <program@koicon.com>'."\n")));
	$smtp->datasend("To: ".$mail."\n");
	$smtp->datasend(encode('MIME-Header-ISO_2022_JP',decode('utf8',
		"Subject: お申込みメールアドレス確認\n")));
	$smtp->datasend("\n");
	$out = encode('7bit-jis', decode('utf8', $mail_out->output));
	$smtp->datasend($out);
	$smtp->dataend();

    $smtp->quit;
} else {
	$html_out = HTML::Template->new(filename => 'phase0-err-tmpl.html');
}
#htmlの生成
	$out = encode('utf8', decode('utf8', $html_out->output));
print $cgi->header(-charset=>'UTF-8');
print "\n\n".$out;
#end

