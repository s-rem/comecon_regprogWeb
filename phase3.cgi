#!/usr/bin/perl
use lib ((getpwuid($<))[7]) . '/local/lib/perl5';
use strict;
use CGI;
use CGI::Session;
use CGI::Carp qw(fatalsToBrowser); 
use HTML::Template;
use HTML::FillInForm;
use Net::SMTP;
use MIME::Base64;
use SFCON::Register;
use SFCON::Register_db;
use Encode::Guess qw/ shiftjis euc-jp 7bit-jis /;
use Encode qw/ encode decode from_to/;

# 工事中なう
my $cgi=CGI->new;
my $uc_page=HTML::Template->new(filename => 'uc.html');
print $cgi->header(-charset=>'UTF-8');
print "\n\n";
print $uc_page->output;

exit;
1;

my $register = SFCON::Register->new;
my $database = SFCON::Register_db->new;

my $sid=$cgi->param('ID')||$cgi->cookie('ID')||undef;
#1.cookieからCGISESSIDを探す
#2.cookieから取れなかったらurlパラメータを探す．
#3.どちらも取得できなかったらundef．
my $session=CGI::Session->new(undef,$sid,{Directory=>$register->session_dir()});

my $input_page=HTML::Template->new(filename => 'phase3-tmpl.html');

#4.取得したセッションidが有効ならそのまま．無効なら別のidを発番．

if(defined $sid && $sid eq $session->id){
#cookieかurlパラメータから値を取得でき，かつ有効なid

	$input_page->param(ID => $session->id);
	my $r_num = sprintf( "%04d", $database->getprogramnumber($session->id, 0));


	my $envfrom = 'program-return@koicon.com';
	my $headfrom = 'program@koicon.com';
	my $sendto = 'program-operation@koicon.com';
	my $carboncopy = 'program@koicon.com';

	# HTMLを生成する。

	$input_page->param(ORGANIZER => $register->html_out_organizer($session));
	$input_page->param(PROGRAM => $register->html_out_program($session));
	$input_page->param(GUEST => $register->html_out_guest($session));
	$input_page->param(COMMENT => $register->html_out_comment($session));
	my $form_out = HTML::FillInForm->new;
	my $html_out = $form_out->fill(
		scalarref => \$input_page->output,
		target => "mailform2",
		fobject => $cgi
	);

	my $mail_text = HTML::Template->new(filename => 'mail-finish-tmpl.txt');
	$mail_text->param(NAME => $session->param('p1_name'));
	$mail_text->param(DATA => $register->mail_text_program($session));
	my $mail_out = decode('utf8',$mail_text->output);
	$mail_out =~ tr/[\x{ff5e}\x{2225}\x{ff0d}\x{ffe0}\x{ffe1}\x{ffe2}]/[\x{301c}\x{2016}\x{2212}\x{00a2}\x{00a3}\x{00ac}]/;

	# 登録者に確認メールを送る

	my $mail = $session->param('email');
	my $smtp = Net::SMTP->new('127.0.0.1');
	my $ftitle = "register".$r_num.".csv";

	$smtp->mail($envfrom);
	$smtp->to($mail);
	$smtp->to($carboncopy);

	$smtp->data();
	$smtp->datasend(encode('MIME-Header-ISO_2022_JP',decode('utf8',
		"From: 第52回日本SF大会 <" . $headfrom . ">"."\n")));
	$smtp->datasend("To: ".$mail."\n");
	$smtp->datasend(encode('MIME-Header-ISO_2022_JP',decode('utf8',
			"Subject: 企画申込完了通知\n")));
	$smtp->datasend("Content-Transfer-Encoding: 7bit\n");
	$smtp->datasend("Content-Type: text/plain; charset=\"ISO-2022-JP\"\n");
	$smtp->datasend("\n");
	my $out = encode('7bit-jis', $mail_out);
	$smtp->datasend($out);
	$smtp->dataend();
	$smtp->quit;


	# TOKON10登録担当者にメールを送る

	$smtp = Net::SMTP->new('127.0.0.1');
	$mail_out = decode('utf8',$register->reg_mail_text_program($session, $r_num));
	$mail_out =~ tr/[\x{ff5e}\x{2225}\x{ff0d}\x{ffe0}\x{ffe1}\x{ffe2}]/[\x{301c}\x{2016}\x{2212}\x{00a2}\x{00a3}\x{00ac}]/;

	$smtp->mail($envfrom);
	$smtp->to($sendto);
	$smtp->to($carboncopy);
	
	$smtp->data();
	$smtp->datasend('Content-Type: Multipart/Mixed; boundary="'.$sid."\"\n");
	$smtp->datasend(encode('MIME-Header-ISO_2022_JP',decode('utf8',
		"From: 第52回日本SF大会 <" . $headfrom . ">"."\n")));
	$smtp->datasend(encode('MIME-Header-ISO_2022_JP',decode('utf8','To: 企画担当 <' . $sendto . '>' . "\n")));
	$smtp->datasend(encode('MIME-Header-ISO_2022_JP',decode('utf8',"Subject: [program:".$r_num."] こいこん企画受付\n")));
	$smtp->datasend("\n");
	$smtp->datasend("--$sid\n");
	$smtp->datasend("Content-Transfer-Encoding: 7bit\n");
	$smtp->datasend("Content-Type: text/plain; charset=\"ISO-2022-JP\"\n");
	$smtp->datasend("\n");
	$smtp->datasend(encode('7bit-jis', $mail_out));
	$smtp->datasend("\n");
	$smtp->datasend("--$sid\n");
	$smtp->datasend("Content-Type: application/octet-stream; name=\"$ftitle\"\n");
	$smtp->datasend("Content-Transfer-Encoding: base64\n");
	$smtp->datasend("Content-Disposition: attachment; filename=\"$ftitle\"\n");
	$smtp->datasend("\n");
	$smtp->datasend(MIME::Base64::encode(Jcode->new($mail_out)->s("\x{ff0d}","\x{2212}","g")->s("\x{ff5e}","\x{301c}","g")->sjis));
	$smtp->dataend();
	$smtp->quit;

	print $cgi->header(-charset=>'UTF-8');
	print "\n\n".$html_out ;

	$session->close;
  	$session->delete;

}else{
	if(defined $sid && $sid ne $session->id){
		  $session->close;
		  $session->delete;
	}
    $input_page=HTML::Template->new(filename => 'error.html');
	print $cgi->header(-charset=>'UTF-8');
	print "\n\n";
    print $input_page->output;
}
exit;
1;
#end
