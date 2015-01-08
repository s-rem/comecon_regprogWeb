#!/usr/bin/perl
use lib ((getpwuid($<))[7]) . '/local/lib/perl5';
use strict;
use CGI;
use CGI::Session;
use CGI::Carp qw(fatalsToBrowser); 
use HTML::Template;
use Net::SMTP;
use MIME::Base64;
use SFCON::Register;
use SFCON::Register_db;
use Encode::Guess qw/ shiftjis euc-jp 7bit-jis /;
use Encode qw/ encode decode from_to/;

#定数定義
require('pgreglib.pl');
our %CONDEF_CONST;

my $cgi=CGI->new;
my $register = SFCON::Register->new;
my $database = SFCON::Register_db->new;

# セッションID = urlパラメータ||cookieからCGISESSID||取得できなかったらundef．
my $sid=$cgi->param('ID')||$cgi->cookie('ID')||undef;
my $session=CGI::Session->new(undef,$sid,{Directory=>$register->session_dir()});

my $input_page;

#4.取得したセッションidが有効ならそのまま．無効なら別のidを発番．

if(defined $sid && $sid eq $session->id){
    # 取得したセッションidが有効:登録処理
	my $r_num = sprintf( "%04d", $database->getprogramnumber($session->id, 0));
    my $name = $session->param('p1_name');
	my $mailaddr = $session->param('email');

	# 登録者に送るmail本文の生成
	my $mail_out = HTML::Template->new(filename => 'mail-finish-tmpl.txt');
    $mail_out->param(FULLNAME   => $CONDEF_CONST{'FULLNAME'});
    $mail_out->param(FROMADDR   => $CONDEF_CONST{'ENTADDR'});
    $mail_out->param(TOADDR     => $mailaddr);
    $mail_out->param(NAME       => $name);
    #登録者にmail送信
    my $mbody = $mail_out->output;
    doMailSend( $CONDEF_CONST{'ENVFROM'},
                [ $mailaddr, $CONDEF_CONST{'ENTADDR'}, ],
                $mbody );

	# 企画登録スタッフに送るメールの作成
	$mail_out = HTML::Template->new(filename => 'mail-regist-tmpl.txt');
    $mail_out->param(FULLNAME   => $CONDEF_CONST{'FULLNAME'});
    $mail_out->param(FROMADDR   => $CONDEF_CONST{'ENTADDR'});
    $mail_out->param(TOADDR     => $CONDEF_CONST{'PGSTAFF'});
    $mail_out->param(PGNO       => $r_num);
    $mail_out->param(CONNAME    => $CONDEF_CONST{'CONNAME'});
    $mail_out->param(BODY       => create_reg_mail_body($session, $r_num));

    $mbody = $mail_out->output;
    doMailSend( $CONDEF_CONST{'ENVFROM'},
                [ $CONDEF_CONST{'PGSTAFF'}, $CONDEF_CONST{'ENTADDR'}, ],
                $mbody );
	
	# HTMLを生成する。
    $input_page=HTML::Template->new(filename => 'phase3-tmpl.html');
    # phase2.cgiと共通化
	html_out_organizer($input_page, $session);
	html_out_program($input_page, $session);
	html_out_guest($input_page, $session);
	html_out_comment($input_page, $session);

    # 全処理が完了したのでセッションを削除
	$session->close;
  	$session->delete;

}else{
    # 取得したセッションidが無効:エラー画面表示
    $input_page=HTML::Template->new(filename => 'error.html');
    # 古いセッションを削除
	if(defined $sid && $sid ne $session->id){
		  $session->close;
		  $session->delete;
	}
}
# >>> 工事中
$input_page=HTML::Template->new(filename => 'uc.html');
# <<< 工事中
# 共通のTMPL変数置き換え
$input_page->param(ID => $sid);
$input_page->param(CONNAME   => $CONDEF_CONST{'CONNAME'});
$input_page->param(FULLNAME  => $CONDEF_CONST{'FULLNAME'});
$input_page->param(CONPERIOD => $CONDEF_CONST{'CONPERIOD'});

print $cgi->header(-charset=>'UTF-8');
print "\n\n";
print $input_page->output;

exit;

sub create_reg_mail_body {
    return("");
}

sub html_out_organizer {
}

sub html_out_program{
}

sub html_out_guest{
}

sub html_out_comment{
}

1;
#end
